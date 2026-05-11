from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class Phase1AcceptanceDocsTest(unittest.TestCase):
    def test_acceptance_and_roadmap_docs_exist(self):
        required = [
            "docs/architecture/phase1_acceptance.md",
            "docs/architecture/telemetry_column_provenance.md",
            "docs/architecture/runtime_console_output_contract.md",
            "docs/roadmap/gui_frontend_dashboard.md",
        ]

        for relative_path in required:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_phase1_acceptance_states_required_boundaries(self):
        text = read_doc("docs/architecture/phase1_acceptance.md").lower()

        self.assertIn("6f36888", text)
        self.assertIn("13. phase 1 acceptance", text)
        self.assertIn("gstreamer is an integration/demo path", text)
        self.assertIn("not benchmark-grade", text)
        self.assertIn("fakesink", text)
        self.assertIn("faster than real time", text)
        self.assertIn("visible playback", text)
        self.assertIn("not academic benchmark validity", text)
        self.assertIn("fake media engine is the controlled path", text)
        self.assertIn("segment_telemetry.csv", text)
        self.assertIn("evaluation_segments.csv", text)
        self.assertIn("not final benchmark result tables", text)
        self.assertIn("academic abr baselines", text)
        self.assertIn("ai-based abr", text)
        self.assertIn("ppo", text)
        self.assertIn("final qoe metric", text)
        self.assertIn("final reward definition", text)
        self.assertIn("trace infrastructure", text)
        self.assertIn("benchmark scripts", text)
        self.assertIn("gui/operator dashboard", text)
        self.assertIn("return to phase 0 methodology", text)

    def test_gui_roadmap_is_registered_but_bounded(self):
        text = read_doc("docs/roadmap/gui_frontend_dashboard.md").lower()

        self.assertIn("roadmap document only", text)
        self.assertIn("mpd url selection", text)
        self.assertIn("controller selection", text)
        self.assertIn("media engine selection", text)
        self.assertIn("headless/visible playback", text)
        self.assertIn("live human-readable progress", text)
        self.assertIn("segment_telemetry.csv", text)
        self.assertIn("evaluation_segments.csv", text)
        self.assertIn("the gui is not benchmark authority", text)
        self.assertIn("cli/config/run artifacts remain canonical", text)
        self.assertIn("must not silently mix fake and gstreamer", text)
        self.assertIn("must not train ai", text)
        self.assertIn("must not define final qoe or reward", text)

    def test_current_docs_do_not_make_legacy_dataset_names_canonical(self):
        current_docs = [
            "README.md",
            "docs/architecture/phase1_acceptance.md",
            "docs/architecture/output_artifact_contract.md",
            "docs/runbooks/run_layout.md",
        ]

        for relative_path in current_docs:
            text = read_doc(relative_path).lower()
            if "dataset.csv" in text or "dataset_training.csv" in text:
                self.assertIn("deprecated", text, relative_path)
                self.assertNotIn("dataset.csv` is the current canonical", text, relative_path)
                self.assertNotIn("dataset_training.csv` is the current canonical", text, relative_path)


if __name__ == "__main__":
    unittest.main()
