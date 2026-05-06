from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.client_config import (
    DEFAULT_EXAMPLE_CONFIG,
    ClientConfig,
    ConfigError,
    load_client_config,
    validate_config_for_run,
)
from core.controller.max_quality_controller import MaxQualityController
from core.controller.registry import create_controller


class ConfigLoadingTest(unittest.TestCase):
    def test_example_config_loads_without_gstreamer(self):
        config = load_client_config(DEFAULT_EXAMPLE_CONFIG, defaults_path=None)

        self.assertEqual("", config.mpd_url)
        self.assertEqual("fake", config.media_engine.name)
        self.assertEqual("max_quality", config.controller.name)
        self.assertEqual({"debug": False}, config.controller.params)
        self.assertTrue(config.playback.headless)
        self.assertEqual(0, config.playback.initial_quality)
        self.assertFalse(config.playback.initial_controller_decision)
        self.assertEqual("logs", config.output.root_dir)

    def test_local_config_overlays_example_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            defaults = tmp_path / "client.example.yaml"
            local = tmp_path / "client.local.yaml"
            defaults.write_text(
                "\n".join(
                    [
                        'mpd_url: ""',
                        "media_engine:",
                        '  name: "fake"',
                        "  min_queue_time: 1.0",
                        "controller:",
                        '  name: "max_quality"',
                        "  params:",
                        "    debug: false",
                        "playback:",
                        "  initial_quality: 0",
                        "  headless: true",
                        "output:",
                        '  root_dir: "logs"',
                    ]
                ),
                encoding="utf-8",
            )
            local.write_text(
                "\n".join(
                    [
                        'mpd_url: "http://example.invalid/video.mpd"',
                        "playback:",
                        "  initial_quality: 2",
                        "  headless: false",
                        "output:",
                        '  root_dir: "tmp_runs"',
                    ]
                ),
                encoding="utf-8",
            )

            config = load_client_config(local, defaults_path=defaults)

        self.assertEqual("http://example.invalid/video.mpd", config.mpd_url)
        self.assertEqual("fake", config.media_engine.name)
        self.assertEqual("max_quality", config.controller.name)
        self.assertEqual(2, config.playback.initial_quality)
        self.assertFalse(config.playback.headless)
        self.assertEqual("tmp_runs", config.output.root_dir)

    def test_run_validation_requires_mpd_url(self):
        config = ClientConfig.from_dict({"mpd_url": ""})

        with self.assertRaises(ConfigError):
            validate_config_for_run(config)


class ControllerConfigLookupTest(unittest.TestCase):
    def test_registry_creates_controller_from_config_name_and_params(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "controller": {
                    "name": "max_quality",
                    "params": {"debug": False},
                },
            }
        )

        controller = create_controller(config.controller.name, config.controller.params)

        self.assertIsInstance(controller, MaxQualityController)
        self.assertFalse(controller.debug)

    def test_unknown_controller_name_fails(self):
        with self.assertRaises(ValueError):
            create_controller("bola")


if __name__ == "__main__":
    unittest.main()
