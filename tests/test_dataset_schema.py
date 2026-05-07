from __future__ import annotations

import unittest

from core.dataset_schema import (
    build_dataset_header,
    build_training_header,
    feedback_column_names,
    validate_unique_columns,
)


class DatasetSchemaTest(unittest.TestCase):
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

    def test_dataset_header_has_unique_names_with_feedback_segment_index(self):
        header = build_dataset_header(["queued_time", "segment_index", "start_segment_request"])

        self.assertEqual(1, header.count("segment_index"))
        self.assertIn("segment_index", header)
        self.assertIn("feedback_segment_index", header)
        self.assertIn("feedback_queued_time", header)
        self.assertEqual(len(header), len(set(header)))

    def test_training_header_has_unique_names(self):
        header = build_training_header()

        self.assertEqual(len(header), len(set(header)))

    def test_duplicate_detection_reports_clear_error(self):
        with self.assertRaisesRegex(RuntimeError, "duplicate column names: segment_index"):
            validate_unique_columns(
                ["segment_index", "timestamp", "segment_index"],
                schema_name="dataset.csv",
            )


if __name__ == "__main__":
    unittest.main()
