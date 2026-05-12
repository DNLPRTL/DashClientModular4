from __future__ import annotations

import unittest
from pathlib import Path

from core.controller.contract import (
    CONTROLLER_API_STATUS,
    CURRENT_FEEDBACK_KEYS,
    FEEDBACK_CANONICAL_ALIASES,
    FEEDBACK_SEMANTIC_STATUS,
    LEGACY_FEEDBACK_KEYS,
    QUALITY_LEVEL_UNIT,
    TARGET_RATE_UNIT,
)
from core.dataset_schema import DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS


ROOT = Path(__file__).resolve().parents[1]


class BaselineEntryContractTest(unittest.TestCase):
    def test_contract_metadata_is_available_to_future_baselines(self):
        self.assertEqual("current_dict_based_compatibility_api", CONTROLLER_API_STATUS)
        self.assertEqual("bytes_per_second", TARGET_RATE_UNIT)
        self.assertEqual("representation_index", QUALITY_LEVEL_UNIT)
        self.assertEqual(CURRENT_FEEDBACK_KEYS, DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS)
        self.assertIn("bwe", LEGACY_FEEDBACK_KEYS)
        self.assertEqual("measured_download_rate", FEEDBACK_CANONICAL_ALIASES["bwe"])
        self.assertEqual("representation_rate", FEEDBACK_CANONICAL_ALIASES["cur_bitrate"])
        self.assertEqual("buffer_seconds", FEEDBACK_CANONICAL_ALIASES["queued_time"])
        self.assertEqual("deprecated_compatibility_alias", FEEDBACK_SEMANTIC_STATUS["bwe"])

    def test_baseline_contract_doc_contains_required_boundaries(self):
        text = (ROOT / "docs/architecture/baseline_entry_contract.md").read_text(encoding="utf-8").lower()

        for phrase in [
            "target rates are bytes per second",
            "quality levels are representation indices",
            "representation ladder source is mpd",
            "fixed_quality and scripted_quality are test/debug only",
            "max_quality is legacy/debug/stress",
            "current dict-based api",
            "legacy keys are classified",
            "must not depend on console output",
            "no debe escribir directamente `segment_telemetry.csv`",
            "no debe cambiar `eval_phase` ni `use_for_eval`",
        ]:
            self.assertIn(phrase, text)

    def test_phase1_closure_docs_are_present_but_bounded(self):
        report = (ROOT / "docs/architecture/client_readiness_report.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Phase 1 client hardening ready to close: YES", report)
        self.assertIn("Ready as technical base for Phase 0: YES", report)
        self.assertIn("Phase 1 client hardening is ready to close", readme)
        self.assertIn("final QoE/reward definitions", readme)


if __name__ == "__main__":
    unittest.main()
