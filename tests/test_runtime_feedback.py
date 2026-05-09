from __future__ import annotations

import unittest

from core.controller.contract import REQUIRED_FEEDBACK_KEYS
from core.runtime_feedback import build_controller_feedback
from player import Player


class _FakeMediaEngine:
    def get_queued_bytes(self):
        return 1234

    def get_queued_time(self):
        return 5.5


class _FakeDownloader:
    pass


class _FakeController:
    name = "fake_controller"


class RuntimeFeedbackTest(unittest.TestCase):
    def test_build_controller_feedback_preserves_contract_key_order(self):
        rates = [100.0, 200.0, 400.0]
        feedback = build_controller_feedback(
            queued_bytes=123,
            queued_time=4.5,
            rates=rates,
            fragment_durations=[1.0, 2.0, 3.0],
            cur_level=1,
            max_level=2,
            downloaded_bytes=999,
            segment_index=7,
            start_segment_request=10.0,
            stop_segment_request=11.0,
            last_size=600,
            last_time=3.0,
        )

        self.assertEqual(list(REQUIRED_FEEDBACK_KEYS), list(feedback.keys()))
        self.assertIs(rates, feedback["rates"])
        self.assertEqual(200.0, feedback["cur_bitrate"])
        self.assertEqual(200.0, feedback["cur_rate"])
        self.assertEqual(400.0, feedback["max_rate"])
        self.assertEqual(100.0, feedback["min_rate"])
        self.assertEqual(2.0, feedback["fragment_duration"])
        self.assertEqual(200.0, feedback["bwe"])

    def test_build_controller_feedback_uses_current_rate_when_throughput_is_missing(self):
        feedback = build_controller_feedback(
            queued_bytes=0,
            queued_time=0.0,
            rates=[100.0, 200.0],
            fragment_durations=[1.0, 2.0],
            cur_level=1,
            max_level=1,
            downloaded_bytes=0,
            segment_index=0,
            start_segment_request=None,
            stop_segment_request=None,
            last_size=0,
            last_time=0.0,
        )

        self.assertEqual(200.0, feedback["bwe"])

    def test_build_controller_feedback_accepts_explicit_fragment_duration(self):
        feedback = build_controller_feedback(
            queued_bytes=0,
            queued_time=0.0,
            rates=[100.0, 200.0],
            fragment_durations=[1.0, 2.0],
            cur_level=1,
            max_level=1,
            downloaded_bytes=0,
            segment_index=0,
            start_segment_request=None,
            stop_segment_request=None,
            last_size=10,
            last_time=2.0,
            fragment_duration=0.25,
        )

        self.assertEqual(0.25, feedback["fragment_duration"])
        self.assertEqual(5.0, feedback["bwe"])

    def test_player_get_feedback_uses_runtime_feedback_builder(self):
        player = Player(
            parser=None,
            media_engine=_FakeMediaEngine(),
            mpd_url="memory://test.mpd",
            downloader=_FakeDownloader(),
            controller=_FakeController(),
        )
        player.rates = [100.0, 200.0]
        player.frag_durations = [1.0, 2.0]
        player.cur_level = 1
        player.max_level = 1
        player.downloaded_bytes = 321
        player.cur_index = 3
        player.start_segment_request = 1.5
        player.stop_segment_request = 2.5

        feedback = player.get_feedback(last_paused=0, last_size=50, last_time=0.5)

        expected = build_controller_feedback(
            queued_bytes=1234,
            queued_time=5.5,
            rates=player.rates,
            fragment_durations=player.frag_durations,
            cur_level=player.cur_level,
            max_level=player.max_level,
            downloaded_bytes=player.downloaded_bytes,
            segment_index=player.cur_index,
            start_segment_request=player.start_segment_request,
            stop_segment_request=player.stop_segment_request,
            last_size=50,
            last_time=0.5,
        )
        self.assertEqual(expected, feedback)


if __name__ == "__main__":
    unittest.main()
