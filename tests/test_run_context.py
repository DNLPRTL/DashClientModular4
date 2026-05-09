from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core.client_config import ClientConfig
from core.output_artifacts import (
    ENVIRONMENT_FILENAME,
    EVALUATION_SEGMENTS_FILENAME,
    RESOLVED_CONFIG_FILENAME,
    RUN_LOG_FILENAME,
    RUN_MANIFEST_FILENAME,
    SEGMENT_TELEMETRY_FILENAME,
)
from core.run_context import create_run_context


class RunContextTest(unittest.TestCase):
    def _config(self, output_root):
        return ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "media_engine": {"name": "fake"},
                "controller": {"name": "max_quality", "params": {"debug": False}},
                "playback": {"headless": True, "initial_quality": 0},
                "output": {
                    "root_dir": str(output_root),
                    "segment_telemetry_filename": SEGMENT_TELEMETRY_FILENAME,
                    "evaluation_segments_filename": EVALUATION_SEGMENTS_FILENAME,
                },
            },
            source_path="config/client.local.yaml",
        )

    def test_creates_run_directory_and_canonical_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = self._config(Path(tmp) / "logs")

            context = create_run_context(config, command_args=["--config", "config/client.local.yaml"])

            self.assertTrue(context.run_dir.is_dir())
            self.assertEqual(SEGMENT_TELEMETRY_FILENAME, context.segment_telemetry_path.name)
            self.assertEqual(EVALUATION_SEGMENTS_FILENAME, context.evaluation_segments_path.name)
            self.assertEqual(RUN_MANIFEST_FILENAME, context.manifest_path.name)
            self.assertEqual(RESOLVED_CONFIG_FILENAME, context.resolved_config_path.name)
            self.assertEqual(ENVIRONMENT_FILENAME, context.environment_path.name)
            self.assertEqual(RUN_LOG_FILENAME, context.log_path.name)
            self.assertEqual(context.segment_telemetry_path, context.dataset_path)
            self.assertEqual(context.evaluation_segments_path, context.training_path)

    def test_writes_manifest_config_and_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = self._config(Path(tmp) / "logs")
            context = create_run_context(config, command_args=["--config", "config/client.local.yaml"])

            with mock.patch("core.run_context.git_metadata", return_value={"commit": "abc123", "branch": "main", "dirty": False}):
                context.write_resolved_config(config)
                context.write_environment()
                context.write_manifest(config, status="completed")

            self.assertTrue(context.resolved_config_path.is_file())
            self.assertTrue(context.environment_path.is_file())
            self.assertTrue(context.manifest_path.is_file())

            manifest = json.loads(context.manifest_path.read_text(encoding="utf-8"))
            for key in [
                "schema_version",
                "run_id",
                "created_at_local",
                "created_at_utc",
                "output_root",
                "run_dir",
                "config_source",
                "command_line_args",
                "python",
                "platform",
                "cwd",
                "git",
                "controller",
                "media_engine",
                "headless",
                "mpd_url",
                "outputs",
            ]:
                self.assertIn(key, manifest)

            self.assertEqual("completed", manifest["status"])
            self.assertEqual("max_quality", manifest["controller"]["name"])
            self.assertEqual("fake", manifest["media_engine"]["name"])
            self.assertEqual(RUN_MANIFEST_FILENAME, manifest["outputs"]["run_manifest"])
            self.assertEqual(RESOLVED_CONFIG_FILENAME, manifest["outputs"]["resolved_config"])
            self.assertEqual(ENVIRONMENT_FILENAME, manifest["outputs"]["environment"])
            self.assertEqual(SEGMENT_TELEMETRY_FILENAME, manifest["outputs"]["segment_telemetry"])
            self.assertEqual(EVALUATION_SEGMENTS_FILENAME, manifest["outputs"]["evaluation_segments"])
            self.assertEqual(RUN_LOG_FILENAME, manifest["outputs"]["run_log"])
            self.assertNotIn("dataset", manifest["outputs"])
            self.assertNotIn("training", manifest["outputs"])
            self.assertFalse(manifest["benchmark_neutrality"]["outputs_are_benchmark_results"])
            self.assertEqual("use_for_eval", manifest["benchmark_neutrality"]["row_eval_gate"])
            self.assertEqual("eval_phase", manifest["benchmark_neutrality"]["eval_phase_column"])
            self.assertFalse(manifest["benchmark_neutrality"]["terminal_drain_stall_is_rebuffering"])
            self.assertFalse(manifest["benchmark_neutrality"]["final_qoe_reward_defined"])
            self.assertFalse(manifest["benchmark_neutrality"]["final_training_dataset_defined"])

            resolved = json.loads(context.resolved_config_path.read_text(encoding="utf-8"))
            self.assertEqual("http://example.invalid/video.mpd", resolved["mpd_url"])

            environment = json.loads(context.environment_path.read_text(encoding="utf-8"))
            self.assertIn("python", environment)
            self.assertIn("package_versions", environment)
            self.assertIn("optional_gstreamer", environment)


if __name__ == "__main__":
    unittest.main()
