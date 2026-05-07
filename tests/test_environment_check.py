from __future__ import annotations

import io
import unittest
from unittest import mock

from scripts import check_environment


class EnvironmentCheckTest(unittest.TestCase):
    def test_import_is_safe_without_gstreamer(self):
        self.assertTrue(hasattr(check_environment, "run_profile"))

    def test_dev_profile_passes_required_checks(self):
        stream = io.StringIO()

        exit_code = check_environment.run_profile("dev", stream=stream)

        self.assertEqual(0, exit_code, stream.getvalue())
        self.assertIn("Project import main", stream.getvalue())
        self.assertIn("Required checks passed.", stream.getvalue())

    def test_dev_profile_does_not_run_gst_checks(self):
        stream = io.StringIO()

        with mock.patch.object(check_environment, "check_gst_profile", side_effect=AssertionError("gst checked")):
            exit_code = check_environment.run_profile("dev", stream=stream)

        self.assertEqual(0, exit_code, stream.getvalue())

    def test_gst_profile_missing_dependencies_warns_without_strict(self):
        stream = io.StringIO()

        with mock.patch.object(check_environment.importlib, "import_module", side_effect=ModuleNotFoundError("No module named 'gi'")):
            with mock.patch.object(check_environment.shutil, "which", return_value=None):
                exit_code = check_environment.run_profile("gst", strict=False, stream=stream)

        output = stream.getvalue()
        self.assertEqual(0, exit_code, output)
        self.assertIn("WARN PyGObject import", output)
        self.assertIn("Required checks passed.", output)

    def test_gst_profile_missing_dependencies_fails_with_strict(self):
        stream = io.StringIO()

        with mock.patch.object(check_environment.importlib, "import_module", side_effect=ModuleNotFoundError("No module named 'gi'")):
            with mock.patch.object(check_environment.shutil, "which", return_value=None):
                exit_code = check_environment.run_profile("gst", strict=True, stream=stream)

        output = stream.getvalue()
        self.assertNotEqual(0, exit_code)
        self.assertIn("FAIL PyGObject import", output)
        self.assertIn("Required failures:", output)

    def test_analysis_profile_missing_dependencies_warns_without_strict(self):
        stream = io.StringIO()

        with mock.patch.object(check_environment.importlib, "import_module", side_effect=ModuleNotFoundError("missing optional")):
            exit_code = check_environment.run_profile("analysis", strict=False, stream=stream)

        output = stream.getvalue()
        self.assertEqual(0, exit_code, output)
        self.assertIn("WARN Python module numpy", output)


if __name__ == "__main__":
    unittest.main()
