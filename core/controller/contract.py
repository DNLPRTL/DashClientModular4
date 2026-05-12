from __future__ import annotations

from numbers import Real
from typing import Iterable, List, Mapping, Sequence


CONTROLLER_CONTRACT_VERSION = "1.0"
CONTROLLER_API_STATUS = "current_dict_based_compatibility_api"

REQUIRED_FEEDBACK_KEYS = (
    "queued_bytes",
    "queued_time",
    "cur_bitrate",
    "bwe",
    "level",
    "max_level",
    "cur_rate",
    "max_rate",
    "min_rate",
    "max_bitrate",
    "min_bitrate",
    "last_fragment_size",
    "last_download_time",
    "downloaded_bytes",
    "fragment_duration",
    "rates",
    "segment_index",
    "start_segment_request",
    "stop_segment_request",
)

CURRENT_FEEDBACK_KEYS = REQUIRED_FEEDBACK_KEYS

FEEDBACK_UNITS = {
    "queued_bytes": "bytes",
    "queued_time": "seconds",
    "cur_bitrate": "bytes_per_second",
    "bwe": "bytes_per_second",
    "level": "quality_level_index",
    "max_level": "quality_level_index",
    "cur_rate": "bytes_per_second",
    "max_rate": "bytes_per_second",
    "min_rate": "bytes_per_second",
    "max_bitrate": "bytes_per_second",
    "min_bitrate": "bytes_per_second",
    "last_fragment_size": "bytes",
    "last_download_time": "seconds",
    "downloaded_bytes": "bytes",
    "fragment_duration": "seconds",
    "rates": "bytes_per_second_list",
    "segment_index": "segment_or_item_index",
    "start_segment_request": "perf_counter_seconds",
    "stop_segment_request": "perf_counter_seconds",
}

TARGET_RATE_UNIT = "bytes_per_second"
QUALITY_LEVEL_UNIT = "representation_index"

LEGACY_FEEDBACK_KEYS = (
    "cur_bitrate",
    "bwe",
    "cur_rate",
    "max_bitrate",
    "min_bitrate",
)

FEEDBACK_CANONICAL_ALIASES = {
    "queued_bytes": "buffer_bytes_estimate",
    "queued_time": "buffer_seconds",
    "cur_bitrate": "representation_rate",
    "bwe": "measured_download_rate",
    "level": "selected_level",
    "max_level": "max_selectable_level",
    "cur_rate": "representation_rate",
    "max_rate": "max_representation_rate",
    "min_rate": "min_representation_rate",
    "max_bitrate": "max_representation_rate",
    "min_bitrate": "min_representation_rate",
    "last_fragment_size": "last_fragment_size_bytes",
    "last_download_time": "last_download_time_seconds",
    "downloaded_bytes": "downloaded_media_bytes_total",
    "fragment_duration": "segment_duration_seconds",
    "rates": "representation_rates",
    "segment_index": "segment_index",
    "start_segment_request": "segment_request_start_perf_counter_seconds",
    "stop_segment_request": "segment_request_stop_perf_counter_seconds",
}

FEEDBACK_SEMANTIC_STATUS = {
    "queued_bytes": "runtime_buffer_signal",
    "queued_time": "runtime_buffer_signal",
    "cur_bitrate": "deprecated_compatibility_alias",
    "bwe": "deprecated_compatibility_alias",
    "level": "controller_input",
    "max_level": "controller_input",
    "cur_rate": "deprecated_compatibility_alias",
    "max_rate": "controller_input",
    "min_rate": "controller_input",
    "max_bitrate": "deprecated_compatibility_alias",
    "min_bitrate": "deprecated_compatibility_alias",
    "last_fragment_size": "downloader_measurement",
    "last_download_time": "downloader_measurement",
    "downloaded_bytes": "player_runtime_state",
    "fragment_duration": "mpd_segment_context",
    "rates": "mpd_ladder_context",
    "segment_index": "player_runtime_state",
    "start_segment_request": "player_runtime_timing",
    "stop_segment_request": "player_runtime_timing",
}


def missing_feedback_keys(feedback: Mapping[str, object]) -> List[str]:
    return [key for key in REQUIRED_FEEDBACK_KEYS if key not in feedback]


def validate_feedback_keys(feedback: Mapping[str, object]) -> None:
    missing = missing_feedback_keys(feedback)
    if missing:
        raise ValueError("Controller feedback is missing required keys: {0}".format(", ".join(missing)))


def validate_rates(rates: Iterable[object]) -> List[float]:
    values = [] if rates is None else list(rates)
    if not values:
        raise ValueError("Controller rates ladder must not be empty.")

    normalized = []
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError("Controller rates ladder contains a non-numeric value at index {0}.".format(index))
        rate = float(value)
        if rate <= 0:
            raise ValueError("Controller rates ladder contains a non-positive value at index {0}.".format(index))
        normalized.append(rate)
    return normalized


def quantize_rate_to_level(rate: object, rates: Sequence[object]) -> int:
    normalized_rates = validate_rates(rates)
    try:
        target_rate = float(rate)
    except (TypeError, ValueError) as exc:
        raise ValueError("Controller target rate must be numeric.") from exc

    new_level = 0
    for index, ladder_rate in enumerate(normalized_rates):
        if target_rate >= ladder_rate:
            new_level = index
    return new_level
