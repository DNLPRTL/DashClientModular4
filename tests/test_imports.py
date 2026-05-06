import importlib
import unittest


REQUIRED_IMPORTS = [
    "main",
    "player",
    "core.client_config",
    "core.parser.dash",
    "core.downloader",
    "core.media_engine.fake",
    "core.media_engine.gst_media_engine",
    "core.controller.registry",
    "core.controller.max_quality_controller",
]


class ImportSmokeTest(unittest.TestCase):
    def test_required_modules_import(self):
        for module_name in REQUIRED_IMPORTS:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)

    def test_controller_registry_exposes_tracked_controller(self):
        registry = importlib.import_module("core.controller.registry")

        self.assertIn("max_quality", registry.CONTROLLER_REGISTRY)
        self.assertEqual(
            ["max_quality"],
            [spec.key for spec in registry.available_controllers()],
        )


if __name__ == "__main__":
    unittest.main()
