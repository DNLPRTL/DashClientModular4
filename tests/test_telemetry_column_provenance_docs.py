from __future__ import annotations

import unittest
from pathlib import Path

from core.dataset_schema import build_evaluation_segments_header, build_segment_telemetry_header
from core.runtime_feedback import build_controller_feedback


ROOT = Path(__file__).resolve().parents[1]


def default_feedback_keys():
    feedback = build_controller_feedback(
        queued_bytes=10,
        queued_time=1.5,
        rates=[100.0, 200.0],
        fragment_durations=[2.0, 2.0],
        cur_level=0,
        max_level=1,
        downloaded_bytes=1000,
        segment_index=0,
        start_segment_request=1.0,
        stop_segment_request=2.0,
        last_size=500,
        last_time=0.5,
        fragment_duration=2.0,
    )
    return list(feedback.keys())


class TelemetryColumnProvenanceDocsTest(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "docs/architecture/telemetry_column_provenance.md").read_text(encoding="utf-8")

    def test_mentions_every_current_csv_column(self):
        segment_columns = build_segment_telemetry_header(default_feedback_keys())
        evaluation_columns = build_evaluation_segments_header()

        for column in sorted(set(segment_columns + evaluation_columns)):
            self.assertIn("`{0}`".format(column), self.text, column)

    def test_mentions_required_high_risk_columns(self):
        required = [
            "feedback_bwe",
            "feedback_cur_bitrate",
            "feedback_cur_rate",
            "feedback_rates",
            "feedback_last_fragment_size",
            "feedback_last_download_time",
            "feedback_downloaded_bytes",
            "feedback_fragment_duration",
            "tp_now",
            "tp_ewma",
            "tp_min_last5",
            "tp_std_last5",
            "buffer_over_seg",
            "headroom",
            "is_upswitch",
            "is_downswitch",
            "switch_magnitude",
            "phase_raw",
            "phase_smooth",
            "policy_name",
            "policy_target_rate",
            "policy_chosen_level",
            "policy_decision_ms",
            "eval_phase",
            "is_preroll",
            "use_for_eval",
            "stall_flag",
            "stall_duration",
        ]

        for column in required:
            self.assertIn("`{0}`".format(column), self.text, column)

    def test_defines_provenance_dimensions_and_statuses(self):
        lower = self.text.lower()

        for phrase in [
            "source module/function",
            "unit",
            "timing/source event",
            "semantic status",
            "direct benchmark use now?",
            "runtime-only",
            "eval-gated",
            "benchmark-neutral",
            "pending methodology",
            "debug/test-only",
            "deprecated/legacy alias",
        ]:
            self.assertIn(phrase, lower)

    def test_provenance_rejects_final_benchmark_or_training_claims(self):
        lower = self.text.lower()

        self.assertIn("does not define final qoe", lower)
        self.assertIn("ai training data", lower)
        self.assertIn("not a final estimator", lower)
        self.assertIn("not automatically qoe stalls", lower)


if __name__ == "__main__":
    unittest.main()
