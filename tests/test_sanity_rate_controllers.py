from __future__ import annotations

import io
import unittest
from unittest import mock

from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.registry import CONTROLLER_REGISTRY, available_controllers, create_controller
from core.controller.sanity_rate import FixedRateController, MaxRateController, MinRateController
from core.controller.scripted_quality import ScriptedQualityController


def feedback(**overrides):
    values = {
        "rates": [100.0, 200.0, 400.0],
        "max_level": 2,
        "level": 1,
        "queued_time": 5.0,
        "bwe": 999999.0,
        "last_fragment_size": 999999,
        "last_download_time": 0.1,
        "fragment_duration": 4.0,
        "segment_index": 3,
    }
    values.update(overrides)
    return values


class SanityControllerRegistryTest(unittest.TestCase):
    def test_formal_sanity_controllers_are_registered(self):
        self.assertIsInstance(create_controller("min_rate"), MinRateController)
        self.assertIsInstance(create_controller("fixed_rate"), FixedRateController)
        self.assertIsInstance(create_controller("max_rate"), MaxRateController)

        registered_keys = {spec.key for spec in available_controllers()}
        self.assertTrue({"min_rate", "fixed_rate", "max_rate"}.issubset(registered_keys))

    def test_min_and_max_rate_ignore_inherited_unused_params(self):
        self.assertIsInstance(create_controller("min_rate", {"level": 0}), MinRateController)
        self.assertIsInstance(create_controller("max_rate", {"level": 0}), MaxRateController)

    def test_existing_debug_and_legacy_controllers_remain_registered(self):
        self.assertIn("fixed_quality", CONTROLLER_REGISTRY)
        self.assertIn("scripted_quality", CONTROLLER_REGISTRY)
        self.assertIn("max_quality", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(create_controller("scripted_quality", {"levels": [0, 1]}), ScriptedQualityController)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


class SanityControllerContractTest(unittest.TestCase):
    def assert_contract_decision(self, controller, expected_rate, expected_level):
        target_rate = controller.calcControlAction()

        self.assertIsInstance(target_rate, float)
        self.assertEqual(float(expected_rate), target_rate)
        self.assertEqual(float(expected_rate), controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(expected_level, controller.quantizeRate(target_rate))

    def test_target_rate_is_bytes_per_second_and_quality_is_representation_index(self):
        controller = create_controller("max_rate")
        controller.setPlayerFeedback(feedback())

        self.assert_contract_decision(controller, expected_rate=400.0, expected_level=2)

    def test_sanity_controllers_do_not_write_console_output(self):
        for name in ["min_rate", "fixed_rate", "max_rate"]:
            with self.subTest(name=name):
                controller = create_controller(name)
                controller.setPlayerFeedback(feedback())

                stream = io.StringIO()
                with mock.patch("sys.stdout", stream):
                    controller.calcControlAction()

                self.assertEqual("", stream.getvalue())


class MinRateControllerTest(unittest.TestCase):
    def test_multi_level_ladder_selects_first_index(self):
        controller = MinRateController()
        controller.setPlayerFeedback(feedback())

        self.assertEqual(100.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_single_representation_selects_index_zero(self):
        controller = MinRateController()
        controller.setPlayerFeedback(feedback(rates=[300.0], max_level=0))

        self.assertEqual(300.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, "bad", 400.0]}, {"rates": [0.0]}]:
            with self.subTest(feedback=fb):
                controller = MinRateController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_ignores_throughput_and_buffer(self):
        controller = MinRateController()
        controller.setPlayerFeedback(feedback(queued_time=0.0, bwe=1.0))
        low_context_rate = controller.calcControlAction()

        controller.setPlayerFeedback(feedback(queued_time=999.0, bwe=999999999.0))
        high_context_rate = controller.calcControlAction()

        self.assertEqual(low_context_rate, high_context_rate)
        self.assertEqual(100.0, high_context_rate)


class MaxRateControllerTest(unittest.TestCase):
    def test_multi_level_ladder_selects_last_available_index(self):
        controller = MaxRateController()
        controller.setPlayerFeedback(feedback())

        self.assertEqual(400.0, controller.calcControlAction())
        self.assertEqual(2, controller.quantizeRate(controller.getControlAction()))

    def test_respects_feedback_max_level(self):
        controller = MaxRateController()
        controller.setPlayerFeedback(feedback(max_level=1))

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_single_representation_selects_index_zero(self):
        controller = MaxRateController()
        controller.setPlayerFeedback(feedback(rates=[300.0], max_level=0))

        self.assertEqual(300.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, object(), 400.0]}, {"rates": [-1.0]}]:
            with self.subTest(feedback=fb):
                controller = MaxRateController()
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_ignores_throughput_and_buffer(self):
        controller = MaxRateController()
        controller.setPlayerFeedback(feedback(queued_time=0.0, bwe=1.0))
        low_context_rate = controller.calcControlAction()

        controller.setPlayerFeedback(feedback(queued_time=999.0, bwe=1.0))
        high_context_rate = controller.calcControlAction()

        self.assertEqual(low_context_rate, high_context_rate)
        self.assertEqual(400.0, high_context_rate)


class FixedRateControllerTest(unittest.TestCase):
    def test_configured_valid_fixed_quality_is_selected(self):
        controller = FixedRateController(level=1)
        controller.setPlayerFeedback(feedback())

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(1, controller.quantizeRate(controller.getControlAction()))

    def test_configured_quality_below_zero_clamps_to_min(self):
        controller = FixedRateController(level=-5)
        controller.setPlayerFeedback(feedback())

        self.assertEqual(100.0, controller.calcControlAction())

    def test_configured_quality_above_max_clamps_to_max(self):
        controller = FixedRateController(level=99)
        controller.setPlayerFeedback(feedback(max_level=1))

        self.assertEqual(200.0, controller.calcControlAction())

    def test_fixed_target_rate_below_min_clamps_to_min(self):
        controller = FixedRateController(target_rate=50.0)
        controller.setPlayerFeedback(feedback())

        self.assertEqual(100.0, controller.calcControlAction())

    def test_fixed_target_rate_above_max_clamps_to_max(self):
        controller = FixedRateController(target_rate=9999.0)
        controller.setPlayerFeedback(feedback(max_level=1))

        self.assertEqual(200.0, controller.calcControlAction())

    def test_missing_config_uses_safe_default_min(self):
        controller = FixedRateController()
        controller.setPlayerFeedback(feedback())

        self.assertEqual(100.0, controller.calcControlAction())

    def test_single_representation_selects_index_zero(self):
        controller = FixedRateController(level=99)
        controller.setPlayerFeedback(feedback(rates=[300.0], max_level=0))

        self.assertEqual(300.0, controller.calcControlAction())
        self.assertEqual(0, controller.quantizeRate(controller.getControlAction()))

    def test_empty_missing_or_malformed_ladder_fails_safely(self):
        for fb in [{}, {"rates": []}, {"rates": [100.0, None]}, {"rates": [100.0, -2.0]}]:
            with self.subTest(feedback=fb):
                controller = FixedRateController(level=1)
                controller.setPlayerFeedback(fb)

                self.assertEqual(0.0, controller.calcControlAction())
                self.assertEqual(0.0, controller.getControlAction())

    def test_ignores_throughput_and_buffer(self):
        controller = FixedRateController(level=1)
        controller.setPlayerFeedback(feedback(queued_time=0.0, bwe=1.0))
        low_context_rate = controller.calcControlAction()

        controller.setPlayerFeedback(feedback(queued_time=999.0, bwe=999999999.0))
        high_context_rate = controller.calcControlAction()

        self.assertEqual(low_context_rate, high_context_rate)
        self.assertEqual(200.0, high_context_rate)


class FixedRateUnitConversionTest(unittest.TestCase):
    def test_target_rate_default_unit_is_bytes_per_second(self):
        controller = FixedRateController(target_rate=2500.0)
        controller.setPlayerFeedback(feedback(rates=[1000.0, 2000.0, 4000.0], max_level=2))

        self.assertEqual(2000.0, controller.calcControlAction())

    def test_target_rate_bits_per_second_converts_to_bytes_per_second(self):
        controller = FixedRateController(target_rate=16000.0, target_rate_unit="bps")
        controller.setPlayerFeedback(feedback(rates=[1000.0, 2000.0, 4000.0], max_level=2))

        self.assertEqual(2000.0, controller.calcControlAction())

    def test_target_rate_kbps_converts_to_bytes_per_second(self):
        controller = FixedRateController(target_rate=16.0, target_rate_unit="kbps")
        controller.setPlayerFeedback(feedback(rates=[1000.0, 2000.0, 4000.0], max_level=2))

        self.assertEqual(2000.0, controller.calcControlAction())


if __name__ == "__main__":
    unittest.main()
