import importlib
import unittest


REQUIRED_IMPORTS = [
    "main",
    "player",
    "core.benchmark_contract",
    "core.client_config",
    "core.output_artifacts",
    "core.run_context",
    "core.runtime_feedback",
    "core.parser.dash",
    "core.downloader",
    "core.media_engine.fake",
    "core.media_engine.gst_media_engine",
    "core.controller.registry",
    "core.controller.bba",
    "core.controller.bola",
    "core.controller.fixed_quality",
    "core.controller.max_quality_controller",
    "core.controller.rate_based",
    "core.controller.sanity_rate",
    "core.controller.scripted_quality",
]


class ImportSmokeTest(unittest.TestCase):
    def test_required_modules_import(self):
        for module_name in REQUIRED_IMPORTS:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)

    def test_controller_registry_exposes_tracked_controller(self):
        registry = importlib.import_module("core.controller.registry")

        expected = {
            "min_rate",
            "fixed_rate",
            "max_rate",
            "rate_based",
            "bba",
            "bola",
            "fixed_quality",
            "scripted_quality",
            "max_quality",
        }

        self.assertTrue(expected.issubset(registry.CONTROLLER_REGISTRY))
        self.assertTrue(expected.issubset({spec.key for spec in registry.available_controllers()}))


if __name__ == "__main__":
    unittest.main()
