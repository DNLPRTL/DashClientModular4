from __future__ import annotations

from typing import Optional, Sequence

from core.controller.contract import CURRENT_FEEDBACK_KEYS


def build_controller_feedback(
    queued_bytes,
    queued_time,
    rates: Sequence[float],
    fragment_durations: Sequence[float],
    cur_level: int,
    max_level: int,
    downloaded_bytes,
    segment_index: int,
    start_segment_request,
    stop_segment_request,
    last_size,
    last_time,
    fragment_duration: Optional[float] = None,
):
    """Build the current dict-based controller feedback payload."""
    cur = rates[cur_level]
    mx, mn = max(rates), min(rates)
    fd = fragment_duration if fragment_duration is not None else fragment_durations[cur_level]

    if last_time and last_size and last_time > 0:
        bwe_measured = float(last_size) / float(last_time)
    else:
        bwe_measured = float(cur)

    feedback = {
        'queued_bytes': queued_bytes,
        'queued_time': queued_time,
        'cur_bitrate': cur,
        'bwe': bwe_measured,
        'level': cur_level,
        'max_level': max_level,
        'cur_rate': cur,
        'max_rate': mx,
        'min_rate': mn,
        'max_bitrate': mx,
        'min_bitrate': mn,
        'last_fragment_size': last_size,
        'last_download_time': last_time,
        'downloaded_bytes': downloaded_bytes,
        'fragment_duration': fd,
        'rates': rates,
        'segment_index': segment_index,
        'start_segment_request': start_segment_request,
        'stop_segment_request': stop_segment_request,
    }
    return {key: feedback[key] for key in CURRENT_FEEDBACK_KEYS}
