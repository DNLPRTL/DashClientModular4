from __future__ import annotations

import unittest

from core.controller.base import BaseController
from core.controller.contract import (
    CONTROLLER_API_STATUS,
    CURRENT_FEEDBACK_KEYS,
    FEEDBACK_CANONICAL_ALIASES,
    FEEDBACK_SEMANTIC_STATUS,
    FEEDBACK_UNITS,
    LEGACY_FEEDBACK_KEYS,
    QUALITY_LEVEL_UNIT,
    REQUIRED_FEEDBACK_KEYS,
    TARGET_RATE_UNIT,
    missing_feedback_keys,
    quantize_rate_to_level,
    validate_feedback_keys,
    validate_rates,
)
from core.controller.max_quality_controller import MaxQualityController


def complete_feedback(**overrides):
    feedback = {
        "queued_bytes": 0,
        "queued_time": 0.0,
        "cur_bitrate": 100.0,
        "bwe": 100.0,
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
        "fragment_duration": 1.0,
        "rates": [100.0, 200.0, 400.0],
        "segment_index": 0,
        "start_segment_request": 1.0,
        "stop_segment_request": 1.0,
    }
    feedback.update(overrides)
    return feedback


class ControllerContractTest(unittest.TestCase):
    def test_required_feedback_keys_include_current_player_feedback(self):
        self.assertEqual(REQUIRED_FEEDBACK_KEYS, CURRENT_FEEDBACK_KEYS)
        for key in [
            "queued_bytes",
            "queued_time",
            "cur_bitrate",
            "bwe",
            "rates",
            "segment_index",
            "start_segment_request",
            "stop_segment_request",
        ]:
            self.assertIn(key, REQUIRED_FEEDBACK_KEYS)

    def test_feedback_units_document_controller_contract(self):
        self.assertEqual("seconds", FEEDBACK_UNITS["queued_time"])
        self.assertEqual("bytes_per_second", FEEDBACK_UNITS["bwe"])
        self.assertEqual("bytes_per_second_list", FEEDBACK_UNITS["rates"])
        self.assertEqual("segment_or_item_index", FEEDBACK_UNITS["segment_index"])
        self.assertEqual("bytes_per_second", TARGET_RATE_UNIT)
        self.assertEqual("representation_index", QUALITY_LEVEL_UNIT)

    def test_contract_exposes_baseline_entry_semantics(self):
        self.assertEqual("current_dict_based_compatibility_api", CONTROLLER_API_STATUS)
        self.assertIn("bwe", LEGACY_FEEDBACK_KEYS)
        self.assertEqual("measured_download_rate", FEEDBACK_CANONICAL_ALIASES["bwe"])
        self.assertEqual("representation_rate", FEEDBACK_CANONICAL_ALIASES["cur_rate"])
        self.assertEqual("buffer_seconds", FEEDBACK_CANONICAL_ALIASES["queued_time"])
        self.assertEqual("representation_rates", FEEDBACK_CANONICAL_ALIASES["rates"])
        self.assertEqual("deprecated_compatibility_alias", FEEDBACK_SEMANTIC_STATUS["bwe"])
        self.assertEqual("mpd_ladder_context", FEEDBACK_SEMANTIC_STATUS["rates"])

    def test_missing_feedback_keys_are_deterministic(self):
        feedback = complete_feedback()
        del feedback["queued_bytes"]
        del feedback["bwe"]
        del feedback["segment_index"]

        self.assertEqual(
            ["queued_bytes", "bwe", "segment_index"],
            missing_feedback_keys(feedback),
        )

    def test_validate_feedback_keys_accepts_complete_feedback(self):
        validate_feedback_keys(complete_feedback())

    def test_validate_feedback_keys_rejects_missing_keys(self):
        feedback = complete_feedback()
        del feedback["rates"]

        with self.assertRaisesRegex(ValueError, "missing required keys: rates"):
            validate_feedback_keys(feedback)

    def test_validate_rates_accepts_valid_ladder(self):
        self.assertEqual([100.0, 200.0, 400.0], validate_rates([100, 200.0, 400]))

    def test_validate_rates_rejects_invalid_ladders(self):
        invalid_ladders = [
            [],
            [100, "200", 400],
            [100, 0, 400],
            [100, -1, 400],
        ]

        for rates in invalid_ladders:
            with self.subTest(rates=rates):
                with self.assertRaises(ValueError):
                    validate_rates(rates)

    def test_quantize_rate_to_level_matches_floor_ladder_semantics(self):
        rates = [100, 200, 400]

        self.assertEqual(0, quantize_rate_to_level(50, rates))
        self.assertEqual(0, quantize_rate_to_level(100, rates))
        self.assertEqual(1, quantize_rate_to_level(200, rates))
        self.assertEqual(1, quantize_rate_to_level(350, rates))
        self.assertEqual(2, quantize_rate_to_level(999, rates))

    def test_base_controller_quantize_rate_uses_contract_semantics(self):
        controller = BaseController()
        self.assertEqual(0, controller.quantizeRate(999))

        controller.setPlayerFeedback({"rates": [100, 200, 400]})

        for target_rate in [50, 100, 199, 200, 350, 999]:
            with self.subTest(target_rate=target_rate):
                self.assertEqual(
                    quantize_rate_to_level(target_rate, [100, 200, 400]),
                    controller.quantizeRate(target_rate),
                )

    def test_max_quality_controller_selects_max_allowed_rate(self):
        controller = MaxQualityController(debug=False)
        controller.setPlayerFeedback(complete_feedback(max_level=1))

        target_rate = controller.calcControlAction()

        self.assertEqual(200.0, target_rate)
        self.assertEqual(200.0, controller.getControlAction())
        self.assertEqual(0.0, controller.getIdleDuration())
        self.assertEqual(1, controller.quantizeRate(target_rate))


if __name__ == "__main__":
    unittest.main()
