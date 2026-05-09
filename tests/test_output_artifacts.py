from __future__ import annotations

import unittest

from core import output_artifacts


class OutputArtifactsTest(unittest.TestCase):
    def test_canonical_filenames(self):
        self.assertEqual("run_manifest.json", output_artifacts.RUN_MANIFEST_FILENAME)
        self.assertEqual("config.resolved.json", output_artifacts.RESOLVED_CONFIG_FILENAME)
        self.assertEqual("environment.json", output_artifacts.ENVIRONMENT_FILENAME)
        self.assertEqual("run.log", output_artifacts.RUN_LOG_FILENAME)
        self.assertEqual("segment_telemetry.csv", output_artifacts.SEGMENT_TELEMETRY_FILENAME)
        self.assertEqual("evaluation_segments.csv", output_artifacts.EVALUATION_SEGMENTS_FILENAME)
        self.assertEqual(("dataset.csv", "dataset_training.csv"), output_artifacts.LEGACY_OUTPUT_FILENAMES)

    def test_canonical_manifest_keys_do_not_use_legacy_dataset_terms(self):
        self.assertEqual(
            (
                "run_manifest",
                "resolved_config",
                "environment",
                "segment_telemetry",
                "evaluation_segments",
                "run_log",
            ),
            output_artifacts.CANONICAL_OUTPUT_KEYS,
        )
        self.assertNotIn("dataset", output_artifacts.CANONICAL_OUTPUT_KEYS)
        self.assertNotIn("training", output_artifacts.CANONICAL_OUTPUT_KEYS)


if __name__ == "__main__":
    unittest.main()
