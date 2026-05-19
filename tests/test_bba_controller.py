from __future__ import annotations

import io
import math
import unittest
from unittest import mock

from core.controller.bba import BbaController
from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.rate_based import RateBasedController
from core.controller.registry import CONTROLLER_REGISTRY, available_controllers, create_controller
from core.controller.sanity_rate import FixedRateController, MaxRateController, MinRateController
from core.controller.scripted_quality import ScriptedQualityController


def feedback(**overrides):
    values = {
        "queued_bytes": 0,
        "queued_time": 10.0,
        "cur_bitrate": 200.0,
        "bwe": 999999.0,
        "level": 1,
        "max_level": 3,
        "cur_rate": 200.0,
        "max_rate": 800.0,
        "min_rate": 100.0,
        "max_bitrate": 800.0,
        "min_bitrate": 100.0,
        "last_fragment_size": 999999,
        "last_download_time": 0.1,
        "downloaded_bytes": 0,
        "fragment_duration": 4.0,
        "rates": [100.0, 200.0, 400.0, 800.0],
        "segment_index": 3,
        "start_segment_request": 1.0,
        "stop_segment_request": 2.0,
    }
    values.update(overrides)
    return values


class BbaRegistryTest(unittest.TestCase):
    def test_bba_is_registered(self):
        self.assertIn("bba", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("bba"), BbaController)
        self.assertIn("bba", {spec.key for spec in available_controllers()})

    def test_existing_controller_names_remain_registered(self):
        self.assertIsInstance(create_controller("min_rate"), MinRateController)
        self.assertIsInstance(create_controller("fixed_rate", {"level": 1}), FixedRateController)
        self.assertIsInstance(create_controller("max_rate"), MaxRateController)
        self.assertIsInstance(create_controller("rate_based"), RateBasedController)
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(create_controller("scripted_quality", {"levels": [0, 1]}), ScriptedQualityController)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


class BbaContractTest(unittest.TestCase):
    def test_return_value_follows_current_controller_api(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=10.0))

        target_rate = controller.calcControlAction()

        self.assertIsInstance(target_rate, float)
        self.assertEqual(200.0, target_rate)
        self.assertEqual(200.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(1, controller.quantizeRate(target_rate))

    def test_target_rate_is_bytes_per_second_and_quality_is_representation_index(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(rates=[1000.0, 2000.0, 4000.0], max_level=2, queued_time=10.0))

        self.assertEqual(2000.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_controller_does_not_write_console_output(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=10.0))

        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            controller.calcControlAction()

        self.assertEqual("", stream.getvalue())


class BbaDecisionTest(unittest.TestCase):
    def test_buffer_below_reservoir_selects_minimum(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=4.99))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_buffer_equal_reservoir_selects_minimum(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=5.0))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_buffer_above_reservoir_plus_cushion_selects_maximum(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=30.0))

        self.assertEqual(800.0, controller.calcControlAction())
        self.assertEqual(3, controller.quantizeRate(controller.getControlAction()))

    def test_buffer_equal_reservoir_plus_cushion_selects_maximum(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=15.0))

        self.assertEqual(800.0, controller.calcControlAction())
        self.assertEqual(3, controller.quantizeRate(controller.getControlAction()))

    def test_mid_buffer_maps_to_deterministic_intermediate_representation(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=10.0))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_near_top_cushion_maps_below_max_until_threshold(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(queued_time=14.9))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_increasing_buffer_gives_non_decreasing_quality_level(self):
        observed_levels = []

        for buffer_s in [0.0, 5.0, 7.0, 10.0, 14.9, 15.0, 30.0]:
            controller = BbaController()
            controller.setPlayerFeedback(feedback(queued_time=buffer_s))
            controller.calcControlAction()
            observed_levels.append(controller.quantizeRate(controller.getControlAction()))

        self.assertEqual(sorted(observed_levels), observed_levels)

    def test_missing_buffer_uses_safe_minimum_fallback(self):
        for fb in [feedback(queued_time=None), _without_key(feedback(), "queued_time")]:
            with self.subTest(feedback=fb):
                controller = BbaController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(100.0, controller.calcControlAction())
                self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_negative_or_non_finite_buffer_uses_safe_minimum_fallback(self):
        for buffer_s in [-1.0, math.inf, -math.inf, math.nan]:
            with self.subTest(buffer_s=buffer_s):
                controller = BbaController()
                controller.setPlayerFeedback(feedback(queued_time=buffer_s))

                self.assertEqual(100.0, controller.calcControlAction())
                self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_invalid_reservoir_or_cushion_falls_back_to_defaults(self):
        controller = BbaController(reservoir_s=-1.0, cushion_s=0.0)
        controller.setPlayerFeedback(feedback(queued_time=10.0))

        self.assertEqual(5.0, controller.reservoir_s)
        self.assertEqual(10.0, controller.cushion_s)
        self.assertEqual(200.0, controller.calcControlAction())

    def test_single_representation_selects_index_zero(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(rates=[250.0], max_level=0, queued_time=999.0))

        self.assertEqual(250.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, "bad", 400.0]}, {"rates": [0.0]}]:
            with self.subTest(feedback=fb):
                controller = BbaController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_respects_feedback_max_level(self):
        controller = BbaController()
        controller.setPlayerFeedback(feedback(max_level=2, queued_time=30.0))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_throughput_fields_do_not_change_decision_when_buffer_is_fixed(self):
        low_throughput = BbaController()
        high_throughput = BbaController()
        low_throughput.setPlayerFeedback(
            feedback(queued_time=10.0, bwe=1.0, last_fragment_size=1, last_download_time=10.0)
        )
        high_throughput.setPlayerFeedback(
            feedback(
                queued_time=10.0,
                bwe=999999999.0,
                last_fragment_size=999999999,
                last_download_time=0.001,
            )
        )

        self.assertEqual(low_throughput.calcControlAction(), high_throughput.calcControlAction())
        self.assertEqual(200.0, high_throughput.getControlAction())


class BbaForbiddenSignalTest(unittest.TestCase):
    def test_forbidden_network_or_server_fields_do_not_change_decision(self):
        base_feedback = feedback(queued_time=10.0)
        forbidden_feedback = feedback(
            queued_time=10.0,
            tcp_rtt=0.001,
            packet_loss=0.5,
            congestion_window=999999,
            server_state={"capacity": 999999999},
            future_bandwidth=999999999.0,
            future_throughput_oracle=999999999.0,
        )

        base = BbaController()
        noisy = BbaController()
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(forbidden_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())

    def test_console_log_and_progress_fields_do_not_change_decision(self):
        base_feedback = feedback(queued_time=10.0)
        noisy_feedback = feedback(
            queued_time=10.0,
            console_output="target max",
            run_log="select high quality",
            progress_label="buffer full",
        )

        base = BbaController()
        noisy = BbaController()
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(noisy_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())


def _without_key(values, key):
    copy = dict(values)
    copy.pop(key, None)
    return copy


if __name__ == "__main__":
    unittest.main()
