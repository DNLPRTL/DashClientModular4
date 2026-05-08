from __future__ import annotations

import unittest

from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.registry import CONTROLLER_REGISTRY, create_controller
from core.controller.scripted_quality import ScriptedQualityController


def feedback(**overrides):
    values = {
        "rates": [100.0, 200.0, 400.0],
        "max_level": 2,
        "segment_index": 0,
        "queued_time": 5.0,
        "bwe": 999999.0,
    }
    values.update(overrides)
    return values


class FixedQualityControllerTest(unittest.TestCase):
    def test_returns_configured_level_rate(self):
        controller = FixedQualityController(level=1)
        controller.setPlayerFeedback(feedback())

        self.assertEqual(200.0, controller.calcControlAction())
        self.assertEqual(200.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())

    def test_clamps_above_available_max_level(self):
        controller = FixedQualityController(level=99)
        controller.setPlayerFeedback(feedback())

        self.assertEqual(400.0, controller.calcControlAction())

    def test_clamps_below_zero(self):
        controller = FixedQualityController(level=-2)
        controller.setPlayerFeedback(feedback())

        self.assertEqual(100.0, controller.calcControlAction())

    def test_respects_feedback_max_level(self):
        controller = FixedQualityController(level=2)
        controller.setPlayerFeedback(feedback(max_level=1))

        self.assertEqual(200.0, controller.calcControlAction())

    def test_handles_missing_or_empty_feedback_safely(self):
        controller = FixedQualityController(level=1)

        self.assertEqual(0.0, controller.calcControlAction())
        self.assertEqual(0.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())

        controller.setPlayerFeedback({"rates": []})
        self.assertEqual(0.0, controller.calcControlAction())
        self.assertEqual(0.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())


class ScriptedQualityControllerTest(unittest.TestCase):
    def test_returns_expected_rates_for_segment_indices(self):
        controller = ScriptedQualityController(levels=[0, 2, 1])

        for segment_index, expected_rate in [(0, 100.0), (1, 400.0), (2, 200.0)]:
            with self.subTest(segment_index=segment_index):
                controller.setPlayerFeedback(feedback(segment_index=segment_index))

                self.assertEqual(expected_rate, controller.calcControlAction())
                self.assertEqual(expected_rate, controller.getControlAction())
                self.assertEqual(0.0, controller.getIdleDuration())

    def test_clamps_scripted_levels_above_available_max_level(self):
        controller = ScriptedQualityController(levels=[99])
        controller.setPlayerFeedback(feedback())

        self.assertEqual(400.0, controller.calcControlAction())

    def test_clamps_scripted_levels_below_zero(self):
        controller = ScriptedQualityController(levels=[-3])
        controller.setPlayerFeedback(feedback())

        self.assertEqual(100.0, controller.calcControlAction())

    def test_respects_feedback_max_level(self):
        controller = ScriptedQualityController(levels=[2])
        controller.setPlayerFeedback(feedback(max_level=1))

        self.assertEqual(200.0, controller.calcControlAction())

    def test_repeat_last_true_reuses_last_scripted_level(self):
        controller = ScriptedQualityController(levels=[0, 2], repeat_last=True)
        controller.setPlayerFeedback(feedback(segment_index=7))

        self.assertEqual(400.0, controller.calcControlAction())

    def test_repeat_last_false_falls_back_to_level_zero_after_script_end(self):
        controller = ScriptedQualityController(levels=[2], repeat_last=False)
        controller.setPlayerFeedback(feedback(segment_index=7))

        self.assertEqual(100.0, controller.calcControlAction())

    def test_missing_invalid_or_negative_segment_index_uses_first_script_entry(self):
        controller = ScriptedQualityController(levels=[1])

        for segment_index in [None, "not-an-index", -1]:
            with self.subTest(segment_index=segment_index):
                controller.setPlayerFeedback(feedback(segment_index=segment_index))

                self.assertEqual(200.0, controller.calcControlAction())

    def test_empty_or_invalid_levels_default_to_level_zero(self):
        for levels in [[], None, "invalid"]:
            with self.subTest(levels=levels):
                controller = ScriptedQualityController(levels=levels)
                controller.setPlayerFeedback(feedback(segment_index=2))

                self.assertEqual(100.0, controller.calcControlAction())

    def test_handles_missing_or_empty_feedback_safely(self):
        controller = ScriptedQualityController(levels=[1])

        self.assertEqual(0.0, controller.calcControlAction())
        self.assertEqual(0.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())

        controller.setPlayerFeedback({"rates": []})
        self.assertEqual(0.0, controller.calcControlAction())
        self.assertEqual(0.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())


class DeterministicControllerRegistryTest(unittest.TestCase):
    def test_registry_can_create_fixed_and_scripted_quality(self):
        self.assertIsInstance(create_controller("fixed_quality", {"level": 1}), FixedQualityController)
        self.assertIsInstance(
            create_controller("scripted_quality", {"levels": [0, 1]}),
            ScriptedQualityController,
        )

    def test_max_quality_remains_registered(self):
        self.assertIn("max_quality", CONTROLLER_REGISTRY)
        self.assertIsInstance(create_controller("max_quality", {"debug": False}), MaxQualityController)


if __name__ == "__main__":
    unittest.main()
