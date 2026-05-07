from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core.client_config import ClientConfig
from core.run_context import create_run_context


class RunContextTest(unittest.TestCase):
    def _config(self, output_root):
        return ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "media_engine": {"name": "fake"},
                "controller": {"name": "max_quality", "params": {"debug": False}},
                "playback": {"headless": True, "initial_quality": 0},
                "output": {"root_dir": str(output_root), "dataset_filename": "dataset.csv"},
            },
            source_path="config/client.local.yaml",
        )

    def test_creates_run_directory_and_canonical_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = self._config(Path(tmp) / "logs")

            context = create_run_context(config, command_args=["--config", "config/client.local.yaml"])

            self.assertTrue(context.run_dir.is_dir())
            self.assertEqual("dataset.csv", context.dataset_path.name)
            self.assertEqual("dataset_training.csv", context.training_path.name)
            self.assertEqual("run_manifest.json", context.manifest_path.name)
            self.assertEqual("config.resolved.json", context.resolved_config_path.name)
            self.assertEqual("environment.json", context.environment_path.name)
            self.assertEqual("run.log", context.log_path.name)

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
            self.assertEqual("dataset.csv", manifest["outputs"]["dataset"])
            self.assertEqual("dataset_training.csv", manifest["outputs"]["training"])

            resolved = json.loads(context.resolved_config_path.read_text(encoding="utf-8"))
            self.assertEqual("http://example.invalid/video.mpd", resolved["mpd_url"])

            environment = json.loads(context.environment_path.read_text(encoding="utf-8"))
            self.assertIn("python", environment)
            self.assertIn("package_versions", environment)
            self.assertIn("optional_gstreamer", environment)


if __name__ == "__main__":
    unittest.main()
