from __future__ import annotations

import io
import unittest
from unittest import mock

from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.rate_based import RateBasedController
from core.controller.registry import CONTROLLER_REGISTRY, available_controllers, create_controller
from core.controller.sanity_rate import FixedRateController, MaxRateController, MinRateController
from core.controller.scripted_quality import ScriptedQualityController


def feedback(**overrides):
    values = {
        "queued_bytes": 0,
        "queued_time": 8.0,
        "cur_bitrate": 200.0,
        "bwe": 0.0,
        "level": 1,
        "max_level": 3,
        "cur_rate": 200.0,
        "max_rate": 800.0,
        "min_rate": 100.0,
        "max_bitrate": 800.0,
        "min_bitrate": 100.0,
        "last_fragment_size": 0,
        "last_download_time": 0.0,
        "downloaded_bytes": 0,
        "fragment_duration": 4.0,
        "rates": [100.0, 200.0, 400.0, 800.0],
        "segment_index": 3,
        "start_segment_request": 1.0,
        "stop_segment_request": 2.0,
    }
    values.update(overrides)
    return values


class RateBasedRegistryTest(unittest.TestCase):
    def test_rate_based_is_registered(self):
        self.assertIn("rate_based", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("rate_based"), RateBasedController)
        self.assertIn("rate_based", {spec.key for spec in available_controllers()})

    def test_existing_controller_names_remain_registered(self):
        self.assertIsInstance(create_controller("min_rate"), MinRateController)
        self.assertIsInstance(create_controller("fixed_rate", {"level": 1}), FixedRateController)
        self.assertIsInstance(create_controller("max_rate"), MaxRateController)
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(create_controller("scripted_quality", {"levels": [0, 1]}), ScriptedQualityController)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


class RateBasedContractTest(unittest.TestCase):
    def test_return_value_follows_current_controller_api(self):
        controller = RateBasedController(safety_factor=0.85)
        controller.setPlayerFeedback(feedback(bwe=300.0))

        target_rate = controller.calcControlAction()

        self.assertIsInstance(target_rate, float)
        self.assertEqual(200.0, target_rate)
        self.assertEqual(200.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(1, controller.quantizeRate(target_rate))

    def test_target_rate_is_bytes_per_second(self):
        controller = RateBasedController(safety_factor=1.0)
        controller.setPlayerFeedback(
            feedback(
                rates=[1000.0, 2000.0, 4000.0],
                max_level=2,
                level=0,
                cur_rate=1000.0,
                cur_bitrate=1000.0,
                measured_throughput_bps=16000.0,
            )
        )

        self.assertEqual(2000.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_controller_does_not_use_console_output(self):
        controller = RateBasedController()
        controller.setPlayerFeedback(feedback(bwe=300.0))

        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            controller.calcControlAction()

        self.assertEqual("", stream.getvalue())


class RateBasedDecisionTest(unittest.TestCase):
    def test_valid_ladder_and_measured_throughput_choose_highest_safe_representation(self):
        controller = RateBasedController(safety_factor=0.85)
        controller.setPlayerFeedback(feedback(bwe=300.0))

        self.assertEqual(200.0, controller.calcControlAction())

    def test_throughput_below_minimum_chooses_minimum_representation(self):
        controller = RateBasedController(safety_factor=0.85)
        controller.setPlayerFeedback(feedback(bwe=90.0, level=2))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_throughput_above_maximum_respects_conservative_upshift(self):
        controller = RateBasedController(safety_factor=1.0)
        controller.setPlayerFeedback(feedback(bwe=2000.0, level=1))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_no_throughput_chooses_startup_minimum_fallback(self):
        controller = RateBasedController()
        controller.setPlayerFeedback(feedback(bwe=0.0, last_fragment_size=0, last_download_time=0.0, level=3))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_zero_or_negative_download_time_falls_back_safely(self):
        for download_time in [0.0, -1.0]:
            with self.subTest(download_time=download_time):
                controller = RateBasedController()
                controller.setPlayerFeedback(
                    feedback(bwe=0.0, last_fragment_size=1200, last_download_time=download_time, level=2)
                )

                self.assertEqual(100.0, controller.calcControlAction())

    def test_direct_bytes_time_throughput_derivation_works(self):
        controller = RateBasedController(safety_factor=0.85)
        controller.setPlayerFeedback(feedback(bwe=0.0, last_fragment_size=1200, last_download_time=4.0))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(300.0, controller.last_metrics["measured_throughput_Bps"])
        self.assertEqual(255.0, controller.last_metrics["safe_throughput_Bps"])

    def test_safety_factor_affects_decision(self):
        conservative = RateBasedController(safety_factor=0.5)
        less_conservative = RateBasedController(safety_factor=1.0)

        conservative.setPlayerFeedback(feedback(bwe=450.0))
        less_conservative.setPlayerFeedback(feedback(bwe=450.0))

        self.assertEqual(200.0, conservative.calcControlAction())
        self.assertEqual(400.0, less_conservative.calcControlAction())

    def test_critical_low_buffer_forces_lower_representation(self):
        controller = RateBasedController(safety_factor=1.0)
        controller.setPlayerFeedback(feedback(bwe=2000.0, level=2, queued_time=1.0))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_throughput_and_ladder_unit_conversions_are_explicit(self):
        controller = RateBasedController(safety_factor=1.0)
        controller.setPlayerFeedback(
            feedback(
                rates=[800.0, 1600.0, 3200.0],
                rates_unit="bits_per_second",
                max_level=2,
                level=0,
                measured_throughput_bps=1600.0,
            )
        )

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, "bad", 400.0]}, {"rates": [0.0]}]:
            with self.subTest(feedback=fb):
                controller = RateBasedController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())


class RateBasedTransitionTest(unittest.TestCase):
    def test_upward_move_is_limited_to_one_level_by_default(self):
        controller = RateBasedController(safety_factor=1.0)
        controller.setPlayerFeedback(feedback(bwe=2000.0, level=0))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_downward_move_can_drop_multiple_levels_when_unsafe(self):
        controller = RateBasedController(safety_factor=1.0)
        controller.setPlayerFeedback(feedback(bwe=180.0, level=3))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_ewma_smooths_upshifts_but_instant_drop_remains_aggressive(self):
        controller = RateBasedController(safety_factor=1.0, ewma_alpha=0.5)

        controller.setPlayerFeedback(feedback(bwe=1200.0, level=3))
        self.assertEqual(800.0, controller.calcControlAction())

        controller.setPlayerFeedback(feedback(bwe=180.0, level=3))
        self.assertEqual(100.0, controller.calcControlAction())

    def test_single_representation_chooses_index_zero(self):
        controller = RateBasedController()
        controller.setPlayerFeedback(feedback(rates=[250.0], max_level=0, level=0, bwe=9999.0))

        self.assertEqual(250.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))


class RateBasedForbiddenSignalTest(unittest.TestCase):
    def test_forbidden_network_or_server_fields_do_not_change_decision(self):
        base_feedback = feedback(bwe=300.0)
        forbidden_feedback = feedback(
            bwe=300.0,
            tcp_rtt=0.001,
            packet_loss=0.5,
            congestion_window=999999,
            server_state={"capacity": 999999999},
            future_throughput_oracle=999999999.0,
        )

        base = RateBasedController()
        noisy = RateBasedController()
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(forbidden_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())

    def test_decision_does_not_require_forbidden_fields(self):
        controller = RateBasedController()
        controller.setPlayerFeedback(feedback(bwe=300.0))

        self.assertEqual(200.0, controller.calcControlAction())


if __name__ == "__main__":
    unittest.main()
