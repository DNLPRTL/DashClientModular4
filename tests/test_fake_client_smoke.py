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
from core.output_artifacts import EVALUATION_SEGMENTS_FILENAME, SEGMENT_TELEMETRY_FILENAME


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
                        '  segment_telemetry_filename: "{0}"'.format(SEGMENT_TELEMETRY_FILENAME),
                        '  evaluation_segments_filename: "{0}"'.format(EVALUATION_SEGMENTS_FILENAME),
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
                segment_telemetry_path = run_dir / SEGMENT_TELEMETRY_FILENAME
                evaluation_segments_path = run_dir / EVALUATION_SEGMENTS_FILENAME
                legacy_dataset_path = run_dir / "dataset.csv"
                legacy_training_path = run_dir / "dataset_training.csv"

                for expected_path in [
                    manifest_path,
                    resolved_config_path,
                    environment_path,
                    log_path,
                    segment_telemetry_path,
                    evaluation_segments_path,
                ]:
                    self.assertTrue(expected_path.is_file(), expected_path)
                self.assertFalse(legacy_dataset_path.exists())
                self.assertFalse(legacy_training_path.exists())

                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual("completed", manifest["status"])
                self.assertEqual("fixed_quality", manifest["controller"]["name"])
                self.assertEqual("fake", manifest["media_engine"]["name"])
                self.assertTrue(manifest["headless"])
                self.assertEqual(SEGMENT_TELEMETRY_FILENAME, manifest["outputs"]["segment_telemetry"])
                self.assertEqual(EVALUATION_SEGMENTS_FILENAME, manifest["outputs"]["evaluation_segments"])
                self.assertNotIn("dataset", manifest["outputs"])
                self.assertNotIn("training", manifest["outputs"])
                self.assertFalse(manifest["benchmark_neutrality"]["outputs_are_benchmark_results"])
                self.assertEqual("use_for_eval", manifest["benchmark_neutrality"]["row_eval_gate"])

                resolved = json.loads(resolved_config_path.read_text(encoding="utf-8"))
                self.assertEqual(mpd_url, resolved["mpd_url"])
                self.assertEqual(SEGMENT_TELEMETRY_FILENAME, resolved["output"]["segment_telemetry_filename"])
                self.assertEqual(EVALUATION_SEGMENTS_FILENAME, resolved["output"]["evaluation_segments_filename"])
                self.assertNotIn("dataset_filename", resolved["output"])

                with segment_telemetry_path.open(newline="", encoding="utf-8") as segment_telemetry_file:
                    segment_telemetry_rows = list(csv.reader(segment_telemetry_file))
                with evaluation_segments_path.open(newline="", encoding="utf-8") as evaluation_segments_file:
                    evaluation_segment_rows = list(csv.reader(evaluation_segments_file))

                self.assertGreaterEqual(len(segment_telemetry_rows), 2)
                self.assertGreaterEqual(len(evaluation_segment_rows), 2)

                segment_telemetry_header = segment_telemetry_rows[0]
                evaluation_segments_header = evaluation_segment_rows[0]
                self.assertEqual(len(segment_telemetry_header), len(set(segment_telemetry_header)))
                self.assertEqual(len(evaluation_segments_header), len(set(evaluation_segments_header)))
                self.assertIn("segment_index", segment_telemetry_header)
                self.assertIn("feedback_segment_index", segment_telemetry_header)
                self.assertIn("feedback_queued_time", segment_telemetry_header)
                self.assertIn("policy_name", segment_telemetry_header)
                self.assertIn("eval_phase", segment_telemetry_header)
                self.assertIn("use_for_eval", segment_telemetry_header)
                self.assertIn("stall_flag", segment_telemetry_header)
                self.assertIn("eval_phase", evaluation_segments_header)
                self.assertIn("use_for_eval", evaluation_segments_header)

                for row in segment_telemetry_rows[1:]:
                    self.assertEqual(len(segment_telemetry_header), len(row))
                for row in evaluation_segment_rows[1:]:
                    self.assertEqual(len(evaluation_segments_header), len(row))

                eval_phase_idx = segment_telemetry_header.index("eval_phase")
                use_for_eval_idx = segment_telemetry_header.index("use_for_eval")
                observed_phases = {row[eval_phase_idx] for row in segment_telemetry_rows[1:]}
                self.assertIn("init", observed_phases)
                self.assertIn("warmup", observed_phases)
                self.assertIn("steady_state", observed_phases)
                for row in segment_telemetry_rows[1:]:
                    if row[eval_phase_idx] != "steady_state":
                        self.assertEqual("0", row[use_for_eval_idx])
                eval_segments_phase_idx = evaluation_segments_header.index("eval_phase")
                eval_segments_use_idx = evaluation_segments_header.index("use_for_eval")
                for row in evaluation_segment_rows[1:]:
                    if row[eval_segments_phase_idx] != "steady_state":
                        self.assertEqual("0", row[eval_segments_use_idx])

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
