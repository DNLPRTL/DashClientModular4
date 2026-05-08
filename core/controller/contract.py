from __future__ import annotations

from numbers import Real
from typing import Iterable, List, Mapping, Sequence


CONTROLLER_CONTRACT_VERSION = "1.0"

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
