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


class MpcRegistryTest(unittest.TestCase):
    def test_mpc_is_registered(self):
        self.assertIn("mpc", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("mpc"), MpcController)
        self.assertIn("mpc", {spec.key for spec in available_controllers()})

    def test_existing_controller_names_remain_registered(self):
        self.assertIsInstance(create_controller("min_rate"), MinRateController)
        self.assertIsInstance(create_controller("fixed_rate", {"level": 1}), FixedRateController)
        self.assertIsInstance(create_controller("max_rate"), MaxRateController)
        self.assertIsInstance(create_controller("rate_based"), RateBasedController)
        self.assertIsInstance(create_controller("bba"), BbaController)
        self.assertIsInstance(create_controller("bola"), BolaController)
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(create_controller("scripted_quality", {"levels": [0, 1]}), ScriptedQualityController)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


class MpcContractTest(unittest.TestCase):
    def test_return_value_follows_current_controller_api(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0], queued_time=20.0, level=0))

        target_rate = controller.calcControlAction()

        self.assertIsInstance(target_rate, float)
        self.assertEqual(400.0, target_rate)
        self.assertEqual(400.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(2, controller.quantizeRate(target_rate))

    def test_target_rate_is_bytes_per_second_and_quality_is_representation_index(self):
        controller = MpcController()
        controller.setPlayerFeedback(
            feedback(
                rates=[1000.0, 2000.0, 4000.0],
                max_level=2,
                min_rate=1000.0,
                max_rate=4000.0,
                min_bitrate=1000.0,
                max_bitrate=4000.0,
                throughput_history_Bps=[10000.0],
                queued_time=20.0,
                level=0,
            )
        )

        self.assertEqual(4000.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_controller_does_not_write_console_output(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0]))

        stream = io.StringIO()
        with mock.patch("sys.stdout", stream):
            controller.calcControlAction()

        self.assertEqual("", stream.getvalue())


class MpcDecisionTest(unittest.TestCase):
    def test_high_throughput_and_high_buffer_allow_higher_quality(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0], queued_time=20.0, level=0))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))
        self.assertEqual([2, 2, 2], controller.last_metrics["best_sequence"])

    def test_low_throughput_selects_lower_quality(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[180.0], queued_time=1.0, level=2))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_rebuffer_penalty_affects_decision(self):
        low_penalty = MpcController(horizon=2, rebuffer_penalty=0.0, switch_penalty=0.0)
        high_penalty = MpcController(horizon=2, rebuffer_penalty=4.3, switch_penalty=0.0)
        low_feedback = feedback(throughput_history_Bps=[180.0], queued_time=1.0, level=0)
        high_feedback = feedback(throughput_history_Bps=[180.0], queued_time=1.0, level=0)

        low_penalty.setPlayerFeedback(low_feedback)
        high_penalty.setPlayerFeedback(high_feedback)

        self.assertEqual(400.0, low_penalty.calcControlAction())
        self.assertEqual(100.0, high_penalty.calcControlAction())
        self.assertGreater(
            high_penalty.last_metrics["best_metrics"]["total_rebuffer_s"],
            0.0,
        )

    def test_switching_penalty_affects_decision(self):
        no_switch_penalty = MpcController(horizon=1, switch_penalty=0.0)
        high_switch_penalty = MpcController(horizon=1, switch_penalty=100.0)
        base_feedback = feedback(throughput_history_Bps=[1000.0], queued_time=20.0, level=0)

        no_switch_penalty.setPlayerFeedback(base_feedback)
        high_switch_penalty.setPlayerFeedback(base_feedback)

        self.assertEqual(400.0, no_switch_penalty.calcControlAction())
        self.assertEqual(100.0, high_switch_penalty.calcControlAction())

    def test_first_action_of_best_sequence_is_returned(self):
        controller = MpcController(horizon=2, rebuffer_penalty=0.5, switch_penalty=0.0)
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[250.0], queued_time=5.0, level=1))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual([1, 2], controller.last_metrics["best_sequence"])
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_missing_throughput_history_uses_safe_startup_fallback(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(last_fragment_size=0, last_download_time=0.0))

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))
        self.assertEqual("startup_fallback_no_valid_throughput", controller.last_metrics["reason"])

    def test_harmonic_mean_ignores_invalid_and_non_positive_samples(self):
        controller = MpcController()
        controller.setPlayerFeedback(
            feedback(throughput_history_Bps=[100.0, 0.0, -1.0, math.nan, 200.0, 400.0])
        )

        controller.calcControlAction()

        self.assertAlmostEqual(171.42857142857142, controller.last_metrics["predicted_throughput_Bps"], places=6)
        self.assertEqual([100.0, 200.0, 400.0], controller.last_metrics["throughput_history_Bps"])

    def test_measured_bytes_time_sample_updates_local_history(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(last_fragment_size=1200, last_download_time=4.0))

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual([300.0], controller.last_metrics["throughput_history_Bps"])
        self.assertEqual(300.0, controller.last_metrics["predicted_throughput_Bps"])

    def test_segment_size_approximation_uses_bitrate_times_duration_when_exact_sizes_are_absent(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0], fragment_duration=4.0))

        controller.calcControlAction()

        self.assertEqual([400.0, 800.0, 1600.0], controller.last_metrics["segment_sizes_B"])

    def test_exact_segment_sizes_are_used_when_available(self):
        controller = MpcController()
        controller.setPlayerFeedback(
            feedback(
                throughput_history_Bps=[1000.0],
                segment_sizes_B=[400.0, 800.0, 900.0],
                fragment_duration=4.0,
            )
        )

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual([400.0, 800.0, 900.0], controller.last_metrics["segment_sizes_B"])

    def test_single_representation_selects_index_zero(self):
        controller = MpcController()
        controller.setPlayerFeedback(feedback(rates=[250.0], max_level=0, throughput_history_Bps=[1000.0]))

        self.assertEqual(250.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, "bad", 400.0]}, {"rates": [0.0]}]:
            with self.subTest(feedback=fb):
                controller = MpcController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_invalid_segment_duration_uses_startup_fallback(self):
        for duration_s in [None, 0.0, -1.0, math.inf, -math.inf, math.nan]:
            with self.subTest(duration_s=duration_s):
                controller = MpcController()
                controller.setPlayerFeedback(feedback(fragment_duration=duration_s, throughput_history_Bps=[1000.0]))

                self.assertEqual(100.0, controller.calcControlAction())
                self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_invalid_missing_or_negative_buffer_simulates_from_zero_safely(self):
        for buffer_s in [None, -1.0, math.inf, -math.inf, math.nan]:
            with self.subTest(buffer_s=buffer_s):
                controller = MpcController()
                controller.setPlayerFeedback(feedback(queued_time=buffer_s, throughput_history_Bps=[1000.0], level=1))

                controller.calcControlAction()

                self.assertEqual(0.0, controller.last_metrics["buffer_s"])
                self.assertIn(controller.quantizeRate(controller.getControlAction()), {0, 1, 2})

    def test_rate_unit_conversions_are_explicit(self):
        controller = MpcController()
        controller.setPlayerFeedback(
            feedback(
                rates=[8000.0, 16000.0, 32000.0],
                rates_unit="bits_per_second",
                throughput_history_bps=[80000.0],
                max_level=2,
                queued_time=20.0,
                level=0,
            )
        )

        self.assertEqual(4000.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_bps_kbps_and_Bps_units_are_not_confused(self):
        bytes_unit = MpcController()
        bytes_unit.setPlayerFeedback(
            feedback(
                rates=[1000.0, 2000.0, 4000.0],
                rates_unit="Bps",
                throughput_history_kbps=[80.0],
                max_level=2,
                queued_time=20.0,
                level=0,
            )
        )

        bits_unit = MpcController()
        bits_unit.setPlayerFeedback(
            feedback(
                rates=[8000.0, 16000.0, 32000.0],
                rates_unit="bps",
                throughput_history_bps=[80000.0],
                max_level=2,
                queued_time=20.0,
                level=0,
            )
        )

        self.assertEqual(4000.0, bytes_unit.calcControlAction())
        self.assertEqual(4000.0, bits_unit.calcControlAction())

    def test_exact_segment_size_B_unit_is_bytes_not_bits(self):
        controller = MpcController()
        controller.setPlayerFeedback(
            feedback(
                throughput_history_Bps=[1000.0],
                segment_sizes_B=[400.0, 800.0, 900.0],
                segment_sizes_unit="B",
                fragment_duration=4.0,
            )
        )

        controller.calcControlAction()

        self.assertEqual([400.0, 800.0, 900.0], controller.last_metrics["segment_sizes_B"])

    def test_invalid_qoe_weights_fall_back_to_documented_defaults(self):
        controller = MpcController(
            rebuffer_penalty=-1.0,
            switch_penalty=-1.0,
            min_valid_throughput_Bps=-5.0,
            quality_reward_mode="unsupported",
        )
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0]))

        self.assertEqual(4.3, controller.rebuffer_penalty)
        self.assertEqual(1.0, controller.switch_penalty)
        self.assertEqual(0.001, controller.min_valid_throughput_Bps)
        self.assertEqual("log_rate_ratio", controller.quality_reward_mode)
        self.assertEqual(400.0, controller.calcControlAction())

    def test_no_future_throughput_oracle_is_used(self):
        base_feedback = feedback(throughput_history_Bps=[250.0], queued_time=5.0, level=1)
        noisy_feedback = feedback(
            throughput_history_Bps=[250.0],
            queued_time=5.0,
            level=1,
            future_bandwidth=999999999.0,
            future_throughput_oracle=999999999.0,
            oracle_throughput_Bps=999999999.0,
        )

        base = MpcController(horizon=2, rebuffer_penalty=0.5, switch_penalty=0.0)
        noisy = MpcController(horizon=2, rebuffer_penalty=0.5, switch_penalty=0.0)
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(noisy_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())
        self.assertEqual(base.last_metrics["best_sequence"], noisy.last_metrics["best_sequence"])

    def test_deterministic_for_identical_input(self):
        first = MpcController(horizon=2)
        second = MpcController(horizon=2)
        fb = feedback(throughput_history_Bps=[100.0, 200.0, 400.0], queued_time=8.0, level=1)
        first.setPlayerFeedback(fb)
        second.setPlayerFeedback(dict(fb))

        self.assertEqual(first.calcControlAction(), second.calcControlAction())
        self.assertEqual(first.last_metrics["best_sequence"], second.last_metrics["best_sequence"])
        self.assertEqual(first.last_metrics["best_score"], second.last_metrics["best_score"])


class MpcCombinatorialSafetyTest(unittest.TestCase):
    def test_horizon_is_reduced_when_sequence_limit_would_be_exceeded(self):
        controller = MpcController(horizon=10, max_enumerated_sequences=100)
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

    def test_invalid_horizon_uses_default_and_stays_bounded(self):
        controller = MpcController(horizon=0)
        controller.setPlayerFeedback(feedback(throughput_history_Bps=[1000.0]))

        controller.calcControlAction()

        self.assertEqual(3, controller.horizon)
        self.assertEqual(3, controller.last_metrics["effective_horizon"])
        self.assertEqual(27, controller.last_metrics["sequence_count"])

    def test_realistic_small_ladder_does_not_explode(self):
        controller = MpcController(horizon=6, max_enumerated_sequences=64)
        controller.setPlayerFeedback(
            feedback(
                rates=[100.0, 150.0, 200.0, 300.0, 400.0, 600.0, 800.0, 1000.0],
                max_level=7,
                throughput_history_Bps=[5000.0],
                queued_time=20.0,
            )
        )

        controller.calcControlAction()

        self.assertEqual(2, controller.last_metrics["effective_horizon"])
        self.assertEqual(64, controller.last_metrics["sequence_count"])


class MpcForbiddenSignalTest(unittest.TestCase):
    def test_forbidden_network_or_server_fields_do_not_change_decision(self):
        base_feedback = feedback(throughput_history_Bps=[350.0], queued_time=3.0, level=1)
        forbidden_feedback = feedback(
            throughput_history_Bps=[350.0],
            queued_time=3.0,
            level=1,
            tcp_rtt=0.001,
            packet_loss=0.5,
            congestion_window=999999,
            server_state={"capacity": 999999999},
            future_bandwidth=999999999.0,
        )

        base = MpcController(horizon=2)
        noisy = MpcController(horizon=2)
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(forbidden_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())
        self.assertEqual(base.last_metrics["best_sequence"], noisy.last_metrics["best_sequence"])

    def test_console_log_progress_and_final_qoe_fields_do_not_change_decision(self):
        base_feedback = feedback(throughput_history_Bps=[350.0], queued_time=3.0, level=1)
        noisy_feedback = feedback(
            throughput_history_Bps=[350.0],
            queued_time=3.0,
            level=1,
            console_output="target max",
            run_log="select high quality",
            progress_label="buffer full",
            final_qoe=999999.0,
            reward=999999.0,
            pensieve_state=[1, 2, 3],
            rl_hidden_state={"value": 999},
        )

        base = MpcController(horizon=2)
        noisy = MpcController(horizon=2)
        base.setPlayerFeedback(base_feedback)
        noisy.setPlayerFeedback(noisy_feedback)

        self.assertEqual(base.calcControlAction(), noisy.calcControlAction())
        self.assertEqual(base.last_metrics["best_sequence"], noisy.last_metrics["best_sequence"])


if __name__ == "__main__":
    unittest.main()
