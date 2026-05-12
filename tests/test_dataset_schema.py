from __future__ import annotations

import unittest

from core.dataset_schema import (
    DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS,
    build_dataset_header,
    build_default_segment_telemetry_header,
    build_evaluation_segments_header,
    build_segment_telemetry_header,
    build_training_header,
    feedback_column_names,
    validate_unique_columns,
)
from core.controller.contract import CURRENT_FEEDBACK_KEYS
from core.output_artifacts import EVALUATION_SEGMENTS_FILENAME, SEGMENT_TELEMETRY_FILENAME


class SegmentTelemetrySchemaTest(unittest.TestCase):
    def test_feedback_keys_are_prefixed_deterministically(self):
        self.assertEqual(
            [
                "feedback_queued_bytes",
                "feedback_queued_time",
                "feedback_segment_index",
                "feedback_feedback_existing",
            ],
            feedback_column_names(
                [
                    "queued_bytes",
                    "queued_time",
                    "segment_index",
                    "feedback_existing",
                ]
            ),
        )

    def test_segment_telemetry_header_has_unique_names_with_feedback_segment_index(self):
        header = build_segment_telemetry_header(["queued_time", "segment_index", "start_segment_request"])

        self.assertEqual(1, header.count("segment_index"))
        self.assertIn("segment_index", header)
        self.assertIn("feedback_segment_index", header)
        self.assertIn("feedback_queued_time", header)
        self.assertIn("eval_phase", header)
        self.assertIn("use_for_eval", header)
        self.assertEqual(len(header), len(set(header)))

    def test_default_segment_telemetry_header_uses_current_feedback_keys(self):
        header = build_default_segment_telemetry_header()

        self.assertEqual(CURRENT_FEEDBACK_KEYS, DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS)
        self.assertIn("feedback_bwe", header)
        self.assertIn("feedback_rates", header)
        self.assertIn("feedback_last_download_time", header)
        self.assertEqual(len(header), len(set(header)))

    def test_evaluation_segments_header_has_unique_names(self):
        header = build_evaluation_segments_header()

        self.assertIn("eval_phase", header)
        self.assertIn("use_for_eval", header)
        self.assertEqual(len(header), len(set(header)))

    def test_legacy_header_aliases_point_to_canonical_builders(self):
        feedback_keys = ["queued_time"]
        self.assertEqual(build_segment_telemetry_header(feedback_keys), build_dataset_header(feedback_keys))
        self.assertEqual(build_evaluation_segments_header(), build_training_header())

    def test_duplicate_detection_reports_clear_error(self):
        with self.assertRaisesRegex(RuntimeError, "duplicate column names: segment_index"):
            validate_unique_columns(
                ["segment_index", "timestamp", "segment_index"],
                schema_name=SEGMENT_TELEMETRY_FILENAME,
            )

    def test_canonical_schema_names_are_clear(self):
        self.assertEqual("segment_telemetry.csv", SEGMENT_TELEMETRY_FILENAME)
        self.assertEqual("evaluation_segments.csv", EVALUATION_SEGMENTS_FILENAME)


if __name__ == "__main__":
    unittest.main()
