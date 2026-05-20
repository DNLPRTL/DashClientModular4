from __future__ import annotations

import io
import math
import unittest
from unittest import mock

from core.controller.bba import BbaController
from core.controller.bola import BolaController
from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.rate_based import RateBasedController
from core.controller.registry import CONTROLLER_REGISTRY, available_controllers, create_controller
from core.controller.sanity_rate import FixedRateController, MaxRateController, MinRateController
from core.controller.scripted_quality import ScriptedQualityController


def feedback(**overrides):
    values = {
        "queued_bytes": 0,
        "queued_time": 12.0,
        "cur_bitrate": 200.0,
        "bwe": 999999.0,
        "level": 1,
        "max_level": 2,
        "cur_rate": 200.0,
        "max_rate": 400.0,
        "min_rate": 100.0,
        "max_bitrate": 400.0,
        "min_bitrate": 100.0,
        "last_fragment_size": 999999,
        "last_download_time": 0.1,
        "downloaded_bytes": 0,
        "fragment_duration": 4.0,
        "rates": [100.0, 200.0, 400.0],
        "segment_index": 3,
        "start_segment_request": 1.0,
        "stop_segment_request": 2.0,
    }
    values.update(overrides)
    return values


class BolaRegistryTest(unittest.TestCase):
    def test_bola_is_registered(self):
        self.assertIn("bola", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("bola"), BolaController)
        self.assertIn("bola", {spec.key for spec in available_controllers()})

    def test_existing_controller_names_remain_registered(self):
        self.assertIsInstance(create_controller("min_rate"), MinRateController)
        self.assertIsInstance(create_controller("fixed_rate", {"level": 1}), FixedRateController)
        self.assertIsInstance(create_controller("max_rate"), MaxRateController)
        self.assertIsInstance(create_controller("rate_based"), RateBasedController)
        self.assertIsInstance(create_controller("bba"), BbaController)
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(create_controller("scripted_quality", {"levels": [0, 1]}), ScriptedQualityController)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


class BolaContractTest(unittest.TestCase):
    def test_return_value_follows_current_controller_api(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=12.0))

        target_rate = controller.calcControlAction()

        self.assertIsInstance(target_rate, float)
        self.assertEqual(200.0, target_rate)
        self.assertEqual(200.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(1, controller.quantizeRate(target_rate))

    def test_target_rate_is_bytes_per_second_and_quality_is_representation_index(self):
        controller = BolaController()
        controller.setPlayerFeedback(
            feedback(
                rates=[1000.0, 2000.0, 4000.0],
                max_level=2,
                min_rate=1000.0,
                max_rate=4000.0,
                min_bitrate=1000.0,
                max_bitrate=4000.0,
                queued_time=12.0,
            )
        )

        self.assertEqual(2000.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_controller_does_not_write_console_output(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=12.0))

        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            controller.calcControlAction()

        self.assertEqual("", stream.getvalue())


class BolaDecisionTest(unittest.TestCase):
    def test_low_buffer_selects_minimum_representation(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=3.0))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))
        self.assertEqual("low_buffer_fallback", controller.last_metrics["reason"])

    def test_higher_buffer_allows_higher_representation_than_low_buffer(self):
        low = BolaController()
        medium = BolaController()
        high = BolaController()
        low.setPlayerFeedback(feedback(queued_time=3.0))
        medium.setPlayerFeedback(feedback(queued_time=12.0))
        high.setPlayerFeedback(feedback(queued_time=24.0))

        low.calcControlAction()
        medium.calcControlAction()
        high.calcControlAction()

        self.assertEqual(0, low.quantizeRate(low.getControlAction()))
        self.assertEqual(1, medium.quantizeRate(medium.getControlAction()))
        self.assertEqual(2, high.quantizeRate(high.getControlAction()))

    def test_deterministic_score_computation(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=12.0))

        self.assertEqual(200.0, controller.calcControlAction())

        scores = controller.last_metrics["scores_by_level"]
        self.assertAlmostEqual(1.0, scores[0], places=6)
        self.assertAlmostEqual(2.2328679514, scores[1], places=6)
        self.assertAlmostEqual(1.9828679514, scores[2], places=6)
        self.assertEqual(1, controller.last_metrics["raw_best_level"])
        self.assertEqual("score_selection", controller.last_metrics["reason"])

    def test_throughput_is_not_required(self):
        controller = BolaController()
        controller.setPlayerFeedback({"queued_time": 12.0, "fragment_duration": 4.0, "rates": [100.0, 200.0, 400.0]})

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_throughput_and_future_bandwidth_fields_do_not_drive_decision(self):
        low_throughput = BolaController()
        high_throughput = BolaController()
        low_throughput.setPlayerFeedback(
            feedback(queued_time=12.0, bwe=1.0, last_fragment_size=1, last_download_time=10.0)
        )
        high_throughput.setPlayerFeedback(
            feedback(
                queued_time=12.0,
                bwe=999999999.0,
                last_fragment_size=999999999,
                last_download_time=0.001,
                future_bandwidth=999999999.0,
                future_throughput_oracle=999999999.0,
            )
        )

        self.assertEqual(low_throughput.calcControlAction(), high_throughput.calcControlAction())
        self.assertEqual(200.0, high_throughput.getControlAction())

    def test_segment_size_approximation_uses_bitrate_times_duration_when_exact_sizes_are_absent(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=12.0))

        controller.calcControlAction()

        self.assertEqual([400.0, 800.0, 1600.0], controller.last_metrics["segment_sizes_B"])
        self.assertEqual([1.0, 2.0, 4.0], controller.last_metrics["size_units_by_level"])

    def test_exact_segment_sizes_are_used_when_available(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=12.0, segment_sizes_B=[400.0, 1000.0, 1200.0]))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))
        self.assertEqual([400.0, 1000.0, 1200.0], controller.last_metrics["segment_sizes_B"])

    def test_invalid_or_missing_buffer_uses_safe_minimum_fallback(self):
        buffers = [None, -1.0, math.inf, -math.inf, math.nan]
        for buffer_s in buffers:
            with self.subTest(buffer_s=buffer_s):
                controller = BolaController()
                controller.setPlayerFeedback(feedback(queued_time=buffer_s))

                self.assertEqual(100.0, controller.calcControlAction())
                self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

        controller = BolaController()
        controller.setPlayerFeedback(_without_key(feedback(), "queued_time"))
        self.assertEqual(100.0, controller.calcControlAction())

    def test_invalid_or_missing_segment_duration_uses_safe_minimum_fallback(self):
        durations = [None, 0.0, -1.0, math.inf, -math.inf, math.nan]
        for duration_s in durations:
            with self.subTest(duration_s=duration_s):
                controller = BolaController()
                controller.setPlayerFeedback(feedback(fragment_duration=duration_s))

                self.assertEqual(100.0, controller.calcControlAction())
                self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

        controller = BolaController()
        controller.setPlayerFeedback(_without_key(feedback(), "fragment_duration"))
        self.assertEqual(100.0, controller.calcControlAction())

    def test_single_representation_selects_index_zero(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(rates=[250.0], max_level=0, queued_time=999.0))

        self.assertEqual(250.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, "bad", 400.0]}, {"rates": [0.0]}]:
            with self.subTest(feedback=fb):
                controller = BolaController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_all_non_positive_scores_fall_back_to_minimum_rate(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(queued_time=200.0))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))
        self.assertEqual("all_non_positive_scores_min_rate_fallback", controller.last_metrics["reason"])

    def test_invalid_bola_params_fall_back_to_documented_defaults(self):
        controller = BolaController(
            bola_v=-1.0,
            gamma=-0.5,
            min_segment_duration_s=0.0,
            utility_mode="unsupported",
            size_mode="unsupported",
        )
        controller.setPlayerFeedback(feedback(queued_time=12.0))

        self.assertEqual(5.0, controller.bola_v)
        self.assertEqual(0.2, controller.bola_gamma)
        self.assertEqual(0.001, controller.min_segment_duration_s)
        self.assertEqual("log_rate_ratio", controller.utility_mode)
        self.assertEqual("exact_or_bitrate_duration", controller.size_mode)
        self.assertEqual(200.0, controller.calcControlAction())

    def test_respects_feedback_max_level(self):
        controller = BolaController()
        controller.setPlayerFeedback(feedback(max_level=1, queued_time=24.0))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_rate_unit_conversions_are_explicit(self):
        controller = BolaController()
        controller.setPlayerFeedback(
            feedback(
                rates=[8000.0, 16000.0, 32000.0],
                rates_unit="bits_per_second",
                max_level=2,
                min_rate=1000.0,
                max_rate=4000.0,
                min_bitrate=1000.0,
                max_bitrate=4000.0,
                queued_time=12.0,
            )
        )

        self.assertEqual(2000.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_current_quality_level_is_not_required(self):
        controller = BolaController()
        controller.setPlayerFeedback(_without_key(feedback(queued_time=12.0), "level"))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))


class BolaForbiddenSignalTest(unittest.TestCase):
    def test_forbidden_network_or_server_fields_do_not_change_decision(self):
        base_feedback = feedback(queued_time=12.0)
        forbidden_feedback = feedback(
            queued_time=12.0,
            tcp_rtt=0.001,
            packet_loss=0.5,
            congestion_window=999999,
            server_state={"capacity": 999999999},
            future_bandwidth=999999999.0,
            future_throughput_oracle=999999999.0,
        )

        base = BolaController()
        noisy = BolaController()
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(forbidden_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())

    def test_console_log_progress_and_rl_fields_do_not_change_decision(self):
        base_feedback = feedback(queued_time=12.0)
        noisy_feedback = feedback(
            queued_time=12.0,
            console_output="target max",
            run_log="select high quality",
            progress_label="buffer full",
            pensieve_state=[1, 2, 3],
            rl_hidden_state={"value": 999},
        )

        base = BolaController()
        noisy = BolaController()
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(noisy_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())


def _without_key(values, key):
    copy = dict(values)
    copy.pop(key, None)
    return copy


if __name__ == "__main__":
    unittest.main()
