from __future__ import annotations

import io
import math
import unittest
from unittest import mock

from core.controller.bba import BbaController
from core.controller.bola import BolaController
from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.mpc import MpcController
from core.controller.rate_based import RateBasedController
from core.controller.registry import CONTROLLER_REGISTRY, available_controllers, create_controller
from core.controller.robust_mpc import RobustMpcController
from core.controller.sanity_rate import FixedRateController, MaxRateController, MinRateController
from core.controller.scripted_quality import ScriptedQualityController


def feedback(**overrides):
    values = {
        "queued_bytes": 0,
        "queued_time": 20.0,
        "cur_bitrate": 200.0,
        "bwe": 0.0,
        "level": 0,
        "max_level": 2,
        "cur_rate": 100.0,
        "max_rate": 400.0,
        "min_rate": 100.0,
        "max_bitrate": 400.0,
        "min_bitrate": 100.0,
        "last_fragment_size": 0,
        "last_download_time": 0.0,
        "downloaded_bytes": 0,
        "fragment_duration": 4.0,
        "rates": [100.0, 200.0, 400.0],
        "segment_index": 3,
        "start_segment_request": 1.0,
        "stop_segment_request": 2.0,
    }
    values.update(overrides)
    return values


class RobustMpcRegistryTest(unittest.TestCase):
    def test_robust_mpc_is_registered(self):
        self.assertIn("robust_mpc", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("robust_mpc"), RobustMpcController)
        self.assertIn("robust_mpc", {spec.key for spec in available_controllers()})

    def test_existing_controller_names_remain_registered(self):
        self.assertIsInstance(create_controller("min_rate"), MinRateController)
        self.assertIsInstance(create_controller("fixed_rate", {"level": 1}), FixedRateController)
        self.assertIsInstance(create_controller("max_rate"), MaxRateController)
        self.assertIsInstance(create_controller("rate_based"), RateBasedController)
        self.assertIsInstance(create_controller("bba"), BbaController)
        self.assertIsInstance(create_controller("bola"), BolaController)
        self.assertIsInstance(create_controller("mpc"), MpcController)
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(create_controller("scripted_quality", {"levels": [0, 1]}), ScriptedQualityController)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


class RobustMpcContractTest(unittest.TestCase):
    def test_return_value_follows_current_controller_api(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(
            feedback(throughput_history_Bps=[1000.0], prediction_error_history=[0.0], queued_time=20.0)
        )

        target_rate = controller.calcControlAction()

        self.assertIsInstance(target_rate, float)
        self.assertEqual(400.0, target_rate)
        self.assertEqual(400.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(2, controller.quantizeRate(target_rate))

    def test_target_rate_is_bytes_per_second_and_quality_is_representation_index(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(
            feedback(
                rates=[1000.0, 2000.0, 4000.0],
                max_level=2,
                min_rate=1000.0,
                max_rate=4000.0,
                min_bitrate=1000.0,
                max_bitrate=4000.0,
                throughput_history_Bps=[10000.0],
                prediction_error_history=[0.0],
                queued_time=20.0,
                level=0,
            )
        )

        self.assertEqual(4000.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_controller_does_not_write_console_output(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0], prediction_error_history=[0.0]))

        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            controller.calcControlAction()

        self.assertEqual("", stream.getvalue())


class RobustMpcCorrectionTest(unittest.TestCase):
    def test_zero_prediction_error_matches_mpc_decision(self):
        fb = feedback(throughput_history_Bps=[1000.0], prediction_error_history=[0.0], queued_time=20.0, level=0)
        robust = RobustMpcController(horizon=2)
        mpc = MpcController(horizon=2)
        robust.setPlayerFeedback(fb)
        mpc.setPlayerFeedback(fb)

        self.assertEqual(mpc.calcControlAction(), robust.calcControlAction())
        self.assertEqual(mpc.last_metrics["best_sequence"], robust.last_metrics["best_sequence"])
        self.assertEqual(1000.0, robust.last_metrics["base_prediction_Bps"])
        self.assertEqual(1000.0, robust.last_metrics["robust_prediction_Bps"])
        self.assertEqual(0.0, robust.last_metrics["prediction_error_max"])

    def test_high_recent_error_is_more_conservative_than_mpc(self):
        fb = feedback(throughput_history_Bps=[350.0], prediction_error_history=[1.0], queued_time=3.0, level=1)
        robust = RobustMpcController(horizon=2)
        mpc = MpcController(horizon=2)
        robust.setPlayerFeedback(fb)
        mpc.setPlayerFeedback(fb)

        mpc_level = mpc.quantizeRate(mpc.calcControlAction())
        robust_level = robust.quantizeRate(robust.calcControlAction())

        self.assertLessEqual(robust_level, mpc_level)
        self.assertEqual(0, robust_level)
        self.assertEqual(175.0, robust.last_metrics["robust_prediction_Bps"])

    def test_insufficient_history_uses_startup_safety_factor(self):
        controller = RobustMpcController(startup_safety_factor=0.85)
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[400.0]))

        controller.calcControlAction()

        self.assertEqual(400.0, controller.last_metrics["base_prediction_Bps"])
        self.assertEqual(340.0, controller.last_metrics["robust_prediction_Bps"])
        self.assertEqual("startup_safety_factor", controller.last_metrics["robust_correction_mode"])

    def test_prediction_error_handles_zero_actual_throughput_safely(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(
            feedback(
                throughput_history_Bps=[400.0],
                predicted_throughput_history_Bps=[100.0],
                actual_throughput_history_Bps=[0.0],
            )
        )

        controller.calcControlAction()

        self.assertEqual([], controller.last_metrics["prediction_error_history"])
        self.assertEqual("startup_safety_factor", controller.last_metrics["robust_correction_mode"])

    def test_robust_prediction_never_exceeds_base_when_error_positive(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[400.0], prediction_error_history=[0.5]))

        controller.calcControlAction()

        self.assertEqual(400.0, controller.last_metrics["base_prediction_Bps"])
        self.assertAlmostEqual(266.6666666666667, controller.last_metrics["robust_prediction_Bps"])
        self.assertLessEqual(
            controller.last_metrics["robust_prediction_Bps"],
            controller.last_metrics["base_prediction_Bps"],
        )

    def test_max_recent_error_uses_bounded_window(self):
        controller = RobustMpcController(prediction_error_window=3)
        controller.setPlayerFeedback(
            feedback(throughput_history_Bps=[400.0], prediction_error_history=[9.0, 0.1, 0.5, 0.2])
        )

        controller.calcControlAction()

        self.assertEqual([0.1, 0.5, 0.2], controller.last_metrics["prediction_error_history"])
        self.assertEqual(0.5, controller.last_metrics["prediction_error_max"])
        self.assertAlmostEqual(266.6666666666667, controller.last_metrics["robust_prediction_Bps"])

    def test_persistent_prediction_error_is_computed_on_next_actual_sample(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(last_fragment_size=1600, last_download_time=4.0, segment_index=1))
        controller.calcControlAction()

        controller.setPlayerFeedback(feedback(last_fragment_size=800, last_download_time=4.0, segment_index=2))
        controller.calcControlAction()

        self.assertAlmostEqual(0.7, controller.last_metrics["prediction_error_history"][-1])
        self.assertAlmostEqual(0.7, controller.last_metrics["prediction_error_max"])
        self.assertEqual("prediction_error_correction", controller.last_metrics["robust_correction_mode"])

    def test_explicit_prediction_and_actual_histories_can_drive_error(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(
            feedback(
                throughput_history_Bps=[400.0],
                predicted_throughput_history_Bps=[100.0, 300.0],
                actual_throughput_history_Bps=[100.0, 150.0],
            )
        )

        controller.calcControlAction()

        self.assertEqual([0.0, 1.0], controller.last_metrics["prediction_error_history"])
        self.assertEqual(1.0, controller.last_metrics["prediction_error_max"])
        self.assertEqual(200.0, controller.last_metrics["robust_prediction_Bps"])

    def test_deterministic_for_identical_input(self):
        fb = feedback(throughput_history_Bps=[100.0, 200.0, 400.0], prediction_error_history=[0.2], queued_time=8.0)
        first = RobustMpcController(horizon=2)
        second = RobustMpcController(horizon=2)
        first.setPlayerFeedback(fb)
        second.setPlayerFeedback(dict(fb))

        self.assertEqual(first.calcControlAction(), second.calcControlAction())
        self.assertEqual(first.last_metrics["best_sequence"], second.last_metrics["best_sequence"])
        self.assertEqual(first.last_metrics["best_score"], second.last_metrics["best_score"])


class RobustMpcCompatibilityTest(unittest.TestCase):
    def test_high_throughput_and_high_buffer_can_select_high_quality(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0], queued_time=20.0, level=0))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_low_throughput_and_low_buffer_select_lower_quality(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[180.0], queued_time=1.0, level=2))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_first_action_of_best_robust_sequence_is_returned(self):
        controller = RobustMpcController(horizon=2, rebuffer_penalty=0.5, switch_penalty=0.0)
        controller.setPlayerFeedback(
            feedback(throughput_history_Bps=[250.0], prediction_error_history=[0.0], queued_time=5.0, level=1)
        )

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual([1, 2], controller.last_metrics["best_sequence"])
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_internal_objective_remains_controller_local(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0]))

        controller.calcControlAction()

        self.assertTrue(controller.last_metrics["internal_objective_only"])
        self.assertFalse(controller.last_metrics["pensieve_implemented"])
        self.assertFalse(controller.last_metrics["rl_or_neural_state_used"])

    def test_single_representation_selects_index_zero(self):
        controller = RobustMpcController()
        controller.setPlayerFeedback(feedback(rates=[250.0], max_level=0, throughput_history_Bps=[1000.0]))

        self.assertEqual(250.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, "bad", 400.0]}, {"rates": [0.0]}]:
            with self.subTest(feedback=fb):
                controller = RobustMpcController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_invalid_segment_duration_uses_startup_fallback(self):
        for duration_s in [None, 0.0, -1.0, math.inf, -math.inf, math.nan]:
            with self.subTest(duration_s=duration_s):
                controller = RobustMpcController()
                controller.setPlayerFeedback(feedback(fragment_duration=duration_s, throughput_history_Bps=[1000.0]))

                self.assertEqual(100.0, controller.calcControlAction())
                self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_invalid_buffer_simulates_from_zero_safely(self):
        for buffer_s in [None, -1.0, math.inf, -math.inf, math.nan]:
            with self.subTest(buffer_s=buffer_s):
                controller = RobustMpcController()
                controller.setPlayerFeedback(feedback(queued_time=buffer_s, throughput_history_Bps=[1000.0], level=1))

                controller.calcControlAction()

                self.assertEqual(0.0, controller.last_metrics["buffer_s"])
                self.assertIn(controller.quantizeRate(controller.getControlAction()), {0, 1, 2})

    def test_invalid_params_fall_back_to_documented_defaults(self):
        controller = RobustMpcController(
            prediction_error_window=0,
            startup_safety_factor=2.0,
            epsilon_throughput_Bps=-5.0,
            rebuffer_penalty=-1.0,
            switch_penalty=-1.0,
        )
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0]))

        self.assertEqual(5, controller.prediction_error_window)
        self.assertEqual(0.85, controller.startup_safety_factor)
        self.assertEqual(0.001, controller.epsilon_throughput_Bps)
        self.assertEqual(4.3, controller.rebuffer_penalty)
        self.assertEqual(1.0, controller.switch_penalty)
        self.assertEqual(400.0, controller.calcControlAction())

    def test_horizon_is_bounded_for_large_ladder(self):
        controller = RobustMpcController(horizon=10, max_enumerated_sequences=100)
        controller.setPlayerFeedback(
            feedback(
                rates=[100.0, 200.0, 400.0, 800.0, 1600.0],
                max_level=4,
                throughput_history_Bps=[5000.0],
                queued_time=20.0,
            )
        )

        controller.calcControlAction()

        self.assertEqual(2, controller.last_metrics["effective_horizon"])
        self.assertEqual(25, controller.last_metrics["sequence_count"])


class RobustMpcForbiddenSignalTest(unittest.TestCase):
    def test_forbidden_network_or_server_fields_do_not_change_decision(self):
        base_feedback = feedback(throughput_history_Bps=[350.0], prediction_error_history=[0.5], queued_time=3.0, level=1)
        forbidden_feedback = feedback(
            throughput_history_Bps=[350.0],
            prediction_error_history=[0.5],
            queued_time=3.0,
            level=1,
            tcp_rtt=0.001,
            packet_loss=0.5,
            congestion_window=999999,
            server_state={"capacity": 999999999},
            future_bandwidth=999999999.0,
            future_throughput_oracle=999999999.0,
        )

        base = RobustMpcController(horizon=2)
        noisy = RobustMpcController(horizon=2)
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(forbidden_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())
        self.assertEqual(base.last_metrics["best_sequence"], noisy.last_metrics["best_sequence"])

    def test_console_log_progress_and_pensieve_rl_fields_do_not_change_decision(self):
        base_feedback = feedback(throughput_history_Bps=[350.0], prediction_error_history=[0.5], queued_time=3.0, level=1)
        noisy_feedback = feedback(
            throughput_history_Bps=[350.0],
            prediction_error_history=[0.5],
            queued_time=3.0,
            level=1,
            console_output="target max",
            run_log="select high quality",
            progress_label="buffer full",
            pensieve_state=[1, 2, 3],
            pensieve_model_output=999999.0,
            rl_hidden_state={"value": 999},
            final_qoe=999999.0,
            reward=999999.0,
        )

        base = RobustMpcController(horizon=2)
        noisy = RobustMpcController(horizon=2)
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(noisy_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())
        self.assertEqual(base.last_metrics["best_sequence"], noisy.last_metrics["best_sequence"])


if __name__ == "__main__":
    unittest.main()
