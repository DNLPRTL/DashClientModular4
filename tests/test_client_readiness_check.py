from __future__ import annotations

import io
import unittest

from scripts import check_client_readiness


class ClientReadinessCheckTest(unittest.TestCase):
    def test_readiness_script_passes_default_mode(self):
        stream = io.StringIO()

        exit_code = check_client_readiness.run_checks(strict=False, stream=stream)

        self.assertEqual(0, exit_code, stream.getvalue())
        self.assertIn("Verdict: PASS", stream.getvalue())

    def test_readiness_script_passes_strict_mode(self):
        stream = io.StringIO()

        exit_code = check_client_readiness.run_checks(strict=True, stream=stream)

        self.assertEqual(0, exit_code, stream.getvalue())
        self.assertIn("WARN: 0", stream.getvalue())
        self.assertIn("Verdict: PASS", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
