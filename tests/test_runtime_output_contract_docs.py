from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeOutputContractDocsTest(unittest.TestCase):
    def setUp(self):
        self.contract = (ROOT / "docs/architecture/runtime_console_output_contract.md").read_text(encoding="utf-8")

    def test_contract_marks_console_as_non_canonical(self):
        lower = self.contract.lower()

        self.assertIn("human-facing diagnostics", lower)
        self.assertIn("not canonical benchmark output", lower)
        self.assertIn("must not be parsed by benchmark scripts", lower)
        self.assertIn("segment_telemetry.csv", lower)
        self.assertIn("evaluation_segments.csv", lower)

    def test_contract_defines_ambiguous_bw_policy_and_preferred_labels(self):
        lower = self.contract.lower()

        self.assertIn("avoid ambiguous labels such as `bw`", lower)
        self.assertIn("target rate", lower)
        self.assertIn("measured download rate", lower)
        self.assertIn("throughput estimate", lower)
        self.assertIn("representation rate", lower)
        self.assertIn("selected level", lower)
        self.assertIn("buffer estimate", lower)
        self.assertIn("eval phase", lower)
        self.assertIn("`bwe`: current controller-contract key", lower)
        self.assertIn("`visible:`", lower)

    def test_current_progress_label_avoids_bw_shorthand(self):
        progress = (ROOT / "progress_bar.py").read_text(encoding="utf-8")

        self.assertNotIn("BW (bwe)", progress)
        self.assertIn("Tasa descarga medida (bwe)", progress)


if __name__ == "__main__":
    unittest.main()
