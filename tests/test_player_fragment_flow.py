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
from core.client_config import ClientConfig
from core.media_engine.fake import FakeMediaEngine
from core.output_artifacts import EVALUATION_SEGMENTS_FILENAME, SEGMENT_TELEMETRY_FILENAME


class RecordingFakeMediaEngine(FakeMediaEngine):
    instances = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pushed = []
        self.__class__.instances.append(self)

    def push_data(self, data, fragment_duration, level=None, caps=None, info=None):
        self.pushed.append(
            {
                "url": (info or {}).get("url"),
                "duration": fragment_duration,
                "size": len(data),
            }
        )
        return super().push_data(data, fragment_duration, level=level, caps=caps, info=info)


class RecordingDownloader:
    instances = []

    def __init__(self, max_retries=3, verbose=False):
        self.max_retries = max_retries
        self.verbose = verbose
        self.on_event = None
        self.requests = []
        self.__class__.instances.append(self)

    def download(self, url, byte_range=None):
        text_url = str(url)
        if text_url.startswith(("http://", "https://")):
            raise AssertionError("External network is not allowed")
        self.requests.append({"url": text_url, "range": byte_range})
        payload = ("payload:" + Path(text_url).name).encode("ascii")
        return payload, {
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

    def get_file_size(self, url):
        raise AssertionError("SegmentList test must not call get_file_size")


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


class PlayerFragmentFlowTest(unittest.TestCase):
    def setUp(self):
        RecordingFakeMediaEngine.instances = []
        RecordingDownloader.instances = []

    def test_scripted_quality_fake_path_preserves_fragment_flow_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mpd_path = tmp_path / "flow.mpd"
            output_root = tmp_path / "runs"
            mpd_path.write_text(_mpd_text(), encoding="utf-8")
            config = _client_config(mpd_path, output_root)

            try:
                with mock.patch.object(main, "SegmentDownloader", RecordingDownloader):
                    with mock.patch.object(main, "FakeMediaEngine", RecordingFakeMediaEngine):
                        with mock.patch("requests.sessions.Session.request", side_effect=AssertionError("External network is not allowed")):
                            with mock.patch("sys.stdout", io.StringIO()):
                                with mock.patch("sys.stderr", io.StringIO()):
                                    main.run_client(config, command_args=["fragment-flow-test"])

                self.assertEqual(1, len(RecordingDownloader.instances))
                self.assertEqual(1, len(RecordingFakeMediaEngine.instances))

                requested_names = [Path(item["url"]).name for item in RecordingDownloader.instances[0].requests]
                self.assertEqual(["init-low.m4s", "low-1.m4s", "low-2.m4s", "high-3.m4s"], requested_names)

                pushed_names = [Path(item["url"]).name for item in RecordingFakeMediaEngine.instances[0].pushed]
                self.assertEqual(requested_names, pushed_names)
                self.assertEqual(0.0, RecordingFakeMediaEngine.instances[0].pushed[0]["duration"])
                self.assertTrue(all(item["duration"] > 0 for item in RecordingFakeMediaEngine.instances[0].pushed[1:]))

                run_dir = _single_run_dir(output_root)
                manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
                self.assertEqual("completed", manifest["status"])
                self.assertEqual("scripted_quality", manifest["controller"]["name"])
                self.assertEqual("fake", manifest["media_engine"]["name"])
                self.assertEqual(SEGMENT_TELEMETRY_FILENAME, manifest["outputs"]["segment_telemetry"])
                self.assertEqual(EVALUATION_SEGMENTS_FILENAME, manifest["outputs"]["evaluation_segments"])
                self.assertNotIn("dataset", manifest["outputs"])
                self.assertNotIn("training", manifest["outputs"])
                self.assertFalse(manifest["benchmark_neutrality"]["outputs_are_benchmark_results"])
                self.assertEqual("use_for_eval", manifest["benchmark_neutrality"]["row_eval_gate"])

                self.assertTrue((run_dir / SEGMENT_TELEMETRY_FILENAME).is_file())
                self.assertTrue((run_dir / EVALUATION_SEGMENTS_FILENAME).is_file())
                self.assertFalse((run_dir / "dataset.csv").exists())
                self.assertFalse((run_dir / "dataset_training.csv").exists())

                self._assert_csv_integrity(run_dir / SEGMENT_TELEMETRY_FILENAME)
                self._assert_csv_integrity(run_dir / EVALUATION_SEGMENTS_FILENAME)
            finally:
                reset_logging()

    def _assert_csv_integrity(self, path):
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        self.assertGreaterEqual(len(rows), 2)
        header = rows[0]
        self.assertEqual(len(header), len(set(header)))
        self.assertIn("eval_phase", header)
        self.assertIn("use_for_eval", header)
        phase_idx = header.index("eval_phase")
        eval_idx = header.index("use_for_eval")
        for row in rows[1:]:
            self.assertEqual(len(header), len(row))
            if row[phase_idx] != "steady_state":
                self.assertEqual("0", row[eval_idx])


def _single_run_dir(output_root):
    run_dirs = sorted(path for path in output_root.iterdir() if path.is_dir() and path.name.startswith("run_"))
    if len(run_dirs) != 1:
        raise AssertionError("Expected one run dir, found {0}".format(run_dirs))
    return run_dirs[0]


def _mpd_text():
    return """<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     minBufferTime="PT0.001S"
     mediaPresentationDuration="PT0.03S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">
  <Period id="0" duration="PT0.03S">
    <AdaptationSet contentType="video" mimeType="video/mp4">
      <Representation id="low" bandwidth="8000" width="16" height="16" codecs="avc1.42E01E">
        <SegmentList timescale="1000" duration="10">
          <Initialization sourceURL="init-low.m4s" />
          <SegmentURL media="low-1.m4s" />
          <SegmentURL media="low-2.m4s" />
          <SegmentURL media="low-3.m4s" />
        </SegmentList>
      </Representation>
      <Representation id="high" bandwidth="16000" width="16" height="16" codecs="avc1.42E01E">
        <SegmentList timescale="1000" duration="10">
          <Initialization sourceURL="init-high.m4s" />
          <SegmentURL media="high-1.m4s" />
          <SegmentURL media="high-2.m4s" />
          <SegmentURL media="high-3.m4s" />
        </SegmentList>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
"""


def _client_config(mpd_path, output_root):
    return ClientConfig.from_dict(
        {
            "mpd_url": mpd_path.as_posix(),
            "media_engine": {
                "name": "fake",
                "min_queue_time": 0.001,
            },
            "controller": {
                "name": "scripted_quality",
                "params": {
                    "levels": [0, 0, 1, 1],
                    "repeat_last": True,
                },
            },
            "playback": {
                "initial_quality": 0,
                "initial_controller_decision": False,
                "headless": True,
                "max_buffer_seconds": 60.0,
                "drain_buffer_sleep_seconds": 0.01,
                "preroll_seconds": 0.0,
            },
            "downloader": {
                "max_retries": 1,
                "verbose": False,
            },
            "output": {
                "root_dir": output_root.as_posix(),
                "segment_telemetry_filename": SEGMENT_TELEMETRY_FILENAME,
                "evaluation_segments_filename": EVALUATION_SEGMENTS_FILENAME,
            },
            "logging": {
                "enabled": True,
                "level": "WARNING",
            },
            "analysis": {
                "enabled": False,
            },
        },
        source_path="<fragment-flow-test>",
    )


if __name__ == "__main__":
    unittest.main()
