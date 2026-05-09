from __future__ import annotations

PHASE_INIT = "init"
PHASE_STARTUP = "startup"
PHASE_WARMUP = "warmup"
PHASE_STEADY_STATE = "steady_state"
PHASE_DRAIN = "drain"
PHASE_TERMINAL = "terminal"
PHASE_ERROR = "error"

SEGMENT_PHASES = (
    PHASE_INIT,
    PHASE_STARTUP,
    PHASE_WARMUP,
    PHASE_STEADY_STATE,
    PHASE_DRAIN,
    PHASE_TERMINAL,
    PHASE_ERROR,
)

STALL_STARTUP = "startup_stall"
STALL_REBUFFER = "rebuffer"
STALL_TERMINAL_DRAIN = "terminal_drain_stall"
STALL_RUNTIME_ONLY = "runtime_only"
STALL_UNKNOWN = "unknown"

STALL_CLASSES = (
    STALL_STARTUP,
    STALL_REBUFFER,
    STALL_TERMINAL_DRAIN,
    STALL_RUNTIME_ONLY,
    STALL_UNKNOWN,
)


def normalize_segment_index(value):
    try:
        segment_index = int(value)
    except (TypeError, ValueError):
        return None
    if segment_index < 0:
        return None
    return segment_index


def classify_segment_phase(
    segment_index,
    total_segments,
    warmup_segments,
    is_init=False,
    drain_active=False,
    success=True,
    startup_active=False,
    warmup_active=None,
):
    segment_index = normalize_segment_index(segment_index)
    total_segments = normalize_segment_index(total_segments)
    warmup_segments = normalize_segment_index(warmup_segments)

    if segment_index is None or total_segments is None or warmup_segments is None:
        return PHASE_ERROR
    if total_segments <= 0:
        return PHASE_ERROR
    if not success:
        return PHASE_ERROR
    if segment_index >= total_segments:
        return PHASE_TERMINAL
    if drain_active:
        return PHASE_DRAIN
    if is_init:
        return PHASE_INIT

    if warmup_active is None:
        warmup_active = segment_index < warmup_segments
    if warmup_active:
        return PHASE_WARMUP
    if startup_active:
        return PHASE_STARTUP
    return PHASE_STEADY_STATE


def should_use_segment_for_eval(phase, success=True, is_init=False):
    if not success or is_init:
        return False
    return phase == PHASE_STEADY_STATE


def classify_stall_event(segment_index, total_segments, drain_active=False, playback_started=True):
    segment_index = normalize_segment_index(segment_index)
    total_segments = normalize_segment_index(total_segments)

    if segment_index is None or total_segments is None:
        return STALL_UNKNOWN
    if total_segments <= 0:
        return STALL_UNKNOWN
    if drain_active:
        return STALL_TERMINAL_DRAIN
    if not playback_started:
        return STALL_STARTUP
    if segment_index >= total_segments:
        return STALL_TERMINAL_DRAIN
    return STALL_REBUFFER


def should_use_stall_for_eval(stall_class):
    return stall_class == STALL_REBUFFER
