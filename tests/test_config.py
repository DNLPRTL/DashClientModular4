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
from core.controller.bba import BbaController
from core.controller.bola import BolaController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.mpc import MpcController
from core.controller.rate_based import RateBasedController
from core.controller.registry import create_controller
from core.controller.sanity_rate import FixedRateController


class ConfigLoadingTest(unittest.TestCase):
    def test_example_config_loads_without_gstreamer(self):
        config = load_client_config(DEFAULT_EXAMPLE_CONFIG, defaults_path=None)

        self.assertEqual("", config.mpd_url)
        self.assertEqual("fake", config.media_engine.name)
        self.assertEqual("fixed_quality", config.controller.name)
        self.assertEqual({"level": 0}, config.controller.params)
        self.assertTrue(config.playback.headless)
        self.assertEqual(0, config.playback.initial_quality)
        self.assertFalse(config.playback.initial_controller_decision)
        self.assertEqual("logs", config.output.root_dir)
        self.assertEqual("segment_telemetry.csv", config.output.segment_telemetry_filename)
        self.assertEqual("evaluation_segments.csv", config.output.evaluation_segments_filename)

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
        self.assertEqual("segment_telemetry.csv", config.output.segment_telemetry_filename)
        self.assertEqual("evaluation_segments.csv", config.output.evaluation_segments_filename)

    def test_legacy_dataset_filename_does_not_preserve_old_default_name(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "output": {"root_dir": "logs", "dataset_filename": "dataset.csv"},
            }
        )

        self.assertEqual("segment_telemetry.csv", config.output.segment_telemetry_filename)
        self.assertEqual("evaluation_segments.csv", config.output.evaluation_segments_filename)
        self.assertNotIn("dataset_filename", config.to_dict()["output"])

    def test_canonical_output_fields_reject_legacy_filenames(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "output": {
                    "segment_telemetry_filename": "old/dataset.csv",
                    "evaluation_segments_filename": "old/dataset_training.csv",
                },
            }
        )

        self.assertEqual("segment_telemetry.csv", config.output.segment_telemetry_filename)
        self.assertEqual("evaluation_segments.csv", config.output.evaluation_segments_filename)

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

    def test_registry_creates_formal_fixed_rate_controller(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "controller": {
                    "name": "fixed_rate",
                    "params": {"level": 1},
                },
            }
        )

        controller = create_controller(config.controller.name, config.controller.params)

        self.assertIsInstance(controller, FixedRateController)

    def test_registry_creates_rate_based_controller(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "controller": {
                    "name": "rate_based",
                    "params": {"safety_factor": 0.85},
                },
            }
        )

        controller = create_controller(config.controller.name, config.controller.params)

        self.assertIsInstance(controller, RateBasedController)

    def test_registry_creates_bba_controller(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "controller": {
                    "name": "bba",
                    "params": {"reservoir_s": 5.0, "cushion_s": 10.0},
                },
            }
        )

        controller = create_controller(config.controller.name, config.controller.params)

        self.assertIsInstance(controller, BbaController)

    def test_registry_creates_bola_controller(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "controller": {
                    "name": "bola",
                    "params": {"bola_v": 5.0, "bola_gamma": 0.2},
                },
            }
        )

        controller = create_controller(config.controller.name, config.controller.params)

        self.assertIsInstance(controller, BolaController)

    def test_registry_creates_mpc_controller(self):
        config = ClientConfig.from_dict(
            {
                "mpd_url": "http://example.invalid/video.mpd",
                "controller": {
                    "name": "mpc",
                    "params": {"horizon": 3, "rebuffer_penalty": 4.3},
                },
            }
        )

        controller = create_controller(config.controller.name, config.controller.params)

        self.assertIsInstance(controller, MpcController)

    def test_unknown_controller_name_fails(self):
        with self.assertRaises(ValueError):
            create_controller("unknown_controller")


if __name__ == "__main__":
    unittest.main()
