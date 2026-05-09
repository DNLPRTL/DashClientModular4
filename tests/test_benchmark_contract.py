from __future__ import annotations

import unittest

from core.benchmark_contract import (
    PHASE_DRAIN,
    PHASE_ERROR,
    PHASE_INIT,
    PHASE_STARTUP,
    PHASE_STEADY_STATE,
    PHASE_TERMINAL,
    PHASE_WARMUP,
    STALL_REBUFFER,
    STALL_STARTUP,
    STALL_TERMINAL_DRAIN,
    STALL_UNKNOWN,
    classify_segment_phase,
    classify_stall_event,
    normalize_segment_index,
    should_use_segment_for_eval,
    should_use_stall_for_eval,
)


class BenchmarkContractTest(unittest.TestCase):
    def test_init_is_non_evaluable(self):
        phase = classify_segment_phase(0, total_segments=3, warmup_segments=1, is_init=True)

        self.assertEqual(PHASE_INIT, phase)
        self.assertFalse(should_use_segment_for_eval(phase, is_init=True))

    def test_warmup_is_non_evaluable(self):
        phase = classify_segment_phase(0, total_segments=3, warmup_segments=1)

        self.assertEqual(PHASE_WARMUP, phase)
        self.assertFalse(should_use_segment_for_eval(phase))

    def test_startup_is_non_evaluable(self):
        phase = classify_segment_phase(1, total_segments=3, warmup_segments=1, startup_active=True)

        self.assertEqual(PHASE_STARTUP, phase)
        self.assertFalse(should_use_segment_for_eval(phase))

    def test_steady_state_successful_segment_is_evaluable(self):
        phase = classify_segment_phase(2, total_segments=4, warmup_segments=1)

        self.assertEqual(PHASE_STEADY_STATE, phase)
        self.assertTrue(should_use_segment_for_eval(phase))

    def test_failed_segment_is_non_evaluable(self):
        phase = classify_segment_phase(2, total_segments=4, warmup_segments=1, success=False)

        self.assertEqual(PHASE_ERROR, phase)
        self.assertFalse(should_use_segment_for_eval(phase, success=False))

    def test_drain_is_non_evaluable(self):
        phase = classify_segment_phase(2, total_segments=4, warmup_segments=1, drain_active=True)

        self.assertEqual(PHASE_DRAIN, phase)
        self.assertFalse(should_use_segment_for_eval(phase))

    def test_terminal_is_non_evaluable(self):
        phase = classify_segment_phase(4, total_segments=4, warmup_segments=1)

        self.assertEqual(PHASE_TERMINAL, phase)
        self.assertFalse(should_use_segment_for_eval(phase))

    def test_terminal_drain_stall_is_non_evaluable(self):
        stall_class = classify_stall_event(3, total_segments=4, drain_active=True)

        self.assertEqual(STALL_TERMINAL_DRAIN, stall_class)
        self.assertFalse(should_use_stall_for_eval(stall_class))

    def test_startup_stall_is_classified_separately_from_rebuffer(self):
        self.assertEqual(
            STALL_STARTUP,
            classify_stall_event(0, total_segments=4, playback_started=False),
        )
        self.assertEqual(
            STALL_REBUFFER,
            classify_stall_event(2, total_segments=4, playback_started=True),
        )

    def test_invalid_segment_index_fails_safe_as_non_evaluable(self):
        phase = classify_segment_phase(None, total_segments=4, warmup_segments=1)

        self.assertIsNone(normalize_segment_index(None))
        self.assertEqual(PHASE_ERROR, phase)
        self.assertFalse(should_use_segment_for_eval(phase))
        self.assertEqual(STALL_UNKNOWN, classify_stall_event(None, total_segments=4))

    def test_helpers_are_deterministic(self):
        args = {
            "segment_index": 2,
            "total_segments": 4,
            "warmup_segments": 1,
            "is_init": False,
            "drain_active": False,
            "success": True,
        }

        self.assertEqual(
            classify_segment_phase(**args),
            classify_segment_phase(**args),
        )
        self.assertEqual(
            classify_stall_event(2, total_segments=4, drain_active=False, playback_started=True),
            classify_stall_event(2, total_segments=4, drain_active=False, playback_started=True),
        )


if __name__ == "__main__":
    unittest.main()
