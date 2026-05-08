from __future__ import annotations

import csv
import io
import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main


class FakeSegmentDownloader:
    instances = []

    def __init__(self, max_retries=3, verbose=False):
        self.max_retries = max_retries
        self.verbose = verbose
        self.on_event = None
        self.downloaded_urls = []
        self.__class__.instances.append(self)

    def download(self, url, byte_range=None):
        text_url = str(url)
        if text_url.startswith(("http://", "https://")):
            raise AssertionError("External HTTP is not allowed in smoke tests")

        self.downloaded_urls.append(text_url)
        payload = "fake segment: {0}".format(text_url.rsplit("/", 1)[-1]).encode("ascii")
        info = {
            "url": text_url,
            "range": byte_range,
            "size": len(payload),
            "status": "ok",
            "elapsed_total": 0.001,
            "elapsed_payload": 0.001,
            "ttfb": 0.0,
            "attempt": 1,
            "saved": False,
            "save_path": None,
            "content_length_header": str(len(payload)),
            "content_range_header": None,
            "aborted": False,
            "bytes_downloaded": len(payload),
        }
        return payload, info

    def get_file_size(self, url):
        raise AssertionError("SegmentList smoke test must not call get_file_size")


def reset_logging():
    logging.shutdown()
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass
    logging.disable(logging.NOTSET)


class FakeClientSmokeTest(unittest.TestCase):
    def test_config_runner_smoke_uses_fake_engine_without_network(self):
        FakeSegmentDownloader.instances = []

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mpd_path = tmp_path / "tiny.mpd"
            config_path = tmp_path / "client.smoke.yaml"
            output_root = tmp_path / "runs"
            mpd_url = mpd_path.as_posix()

            mpd_path.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     minBufferTime="PT0.001S"
     mediaPresentationDuration="PT0.02S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">
  <Period id="0" duration="PT0.02S">
    <AdaptationSet contentType="video" mimeType="video/mp4">
      <Representation id="v0" bandwidth="8000" width="16" height="16" codecs="avc1.42E01E">
        <SegmentList timescale="1000" duration="10">
          <Initialization sourceURL="init.m4s" />
          <SegmentURL media="seg1.m4s" />
          <SegmentURL media="seg2.m4s" />
        </SegmentList>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
""",
                encoding="utf-8",
            )
            config_path.write_text(
                "\n".join(
                    [
                        'mpd_url: "{0}"'.format(mpd_url),
                        "media_engine:",
                        '  name: "fake"',
                        "  min_queue_time: 0.001",
                        "controller:",
                        '  name: "fixed_quality"',
                        "  params:",
                        "    level: 0",
                        "playback:",
                        "  initial_quality: 0",
                        "  initial_controller_decision: true",
                        "  headless: true",
                        "  max_buffer_seconds: 60.0",
                        "  drain_buffer_sleep_seconds: 0.01",
                        "  preroll_seconds: 0.0",
                        "downloader:",
                        "  max_retries: 1",
                        "  verbose: false",
                        "output:",
                        '  root_dir: "{0}"'.format(output_root.as_posix()),
                        '  dataset_filename: "dataset.csv"',
                        "logging:",
                        "  enabled: true",
                        '  level: "WARNING"',
                        "analysis:",
                        "  enabled: false",
                    ]
                ),
                encoding="utf-8",
            )

            try:
                with mock.patch.object(main, "SegmentDownloader", FakeSegmentDownloader):
                    with mock.patch(
                        "requests.sessions.Session.request",
                        side_effect=AssertionError("External HTTP is not allowed in smoke tests"),
                    ) as request_mock:
                        with mock.patch("sys.stdout", io.StringIO()):
                            with mock.patch("sys.stderr", io.StringIO()):
                                exit_code = main.main(["--config", str(config_path)])

                self.assertEqual(0, exit_code)
                request_mock.assert_not_called()

                run_dirs = sorted(path for path in output_root.iterdir() if path.is_dir() and path.name.startswith("run_"))
                self.assertEqual(1, len(run_dirs))
                run_dir = run_dirs[0]

                manifest_path = run_dir / "run_manifest.json"
                resolved_config_path = run_dir / "config.resolved.json"
                environment_path = run_dir / "environment.json"
                log_path = run_dir / "run.log"
                dataset_path = run_dir / "dataset.csv"
                training_path = run_dir / "dataset_training.csv"

                for expected_path in [
                    manifest_path,
                    resolved_config_path,
                    environment_path,
                    log_path,
                    dataset_path,
                    training_path,
                ]:
                    self.assertTrue(expected_path.is_file(), expected_path)

                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual("completed", manifest["status"])
                self.assertEqual("fixed_quality", manifest["controller"]["name"])
                self.assertEqual("fake", manifest["media_engine"]["name"])
                self.assertTrue(manifest["headless"])
                self.assertEqual("dataset.csv", manifest["outputs"]["dataset"])
                self.assertEqual("dataset_training.csv", manifest["outputs"]["training"])

                resolved = json.loads(resolved_config_path.read_text(encoding="utf-8"))
                self.assertEqual(mpd_url, resolved["mpd_url"])

                with dataset_path.open(newline="", encoding="utf-8") as dataset_file:
                    dataset_rows = list(csv.reader(dataset_file))
                with training_path.open(newline="", encoding="utf-8") as training_file:
                    training_rows = list(csv.reader(training_file))

                self.assertGreaterEqual(len(dataset_rows), 2)
                self.assertGreaterEqual(len(training_rows), 2)

                dataset_header = dataset_rows[0]
                training_header = training_rows[0]
                self.assertEqual(len(dataset_header), len(set(dataset_header)))
                self.assertEqual(len(training_header), len(set(training_header)))
                self.assertIn("segment_index", dataset_header)
                self.assertIn("feedback_segment_index", dataset_header)
                self.assertIn("feedback_queued_time", dataset_header)
                self.assertIn("policy_name", dataset_header)
                self.assertIn("stall_flag", dataset_header)

                for row in dataset_rows[1:]:
                    self.assertEqual(len(dataset_header), len(row))
                for row in training_rows[1:]:
                    self.assertEqual(len(training_header), len(row))

                self.assertEqual(1, len(FakeSegmentDownloader.instances))
                downloaded_urls = FakeSegmentDownloader.instances[0].downloaded_urls
                for media_name in ["init.m4s", "seg1.m4s", "seg2.m4s"]:
                    self.assertTrue(
                        any(url.endswith(media_name) for url in downloaded_urls),
                        "{0} not downloaded from {1}".format(media_name, downloaded_urls),
                    )
            finally:
                reset_logging()


if __name__ == "__main__":
    unittest.main()
