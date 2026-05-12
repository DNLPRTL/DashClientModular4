from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Sequence

from core.controller.contract import CURRENT_FEEDBACK_KEYS
from core.output_artifacts import EVALUATION_SEGMENTS_FILENAME, SEGMENT_TELEMETRY_FILENAME

SEGMENT_TELEMETRY_SCHEMA_VERSION = "1.1"
EVALUATION_SEGMENTS_SCHEMA_VERSION = "1.1"

SEGMENT_TELEMETRY_ROW_COLUMNS = [
    "segment_index",
    "timestamp",
]

SEGMENT_TELEMETRY_SEGMENT_COLUMNS = [
    "is_init",
    "retry_count",
    "segment_start_time",
    "segment_end_time",
    "wall_time_elapsed",
]

SEGMENT_TELEMETRY_DERIVED_COLUMNS = [
    "tp_now",
    "tp_ewma",
    "tp_min_last5",
    "tp_std_last5",
    "buffer_over_seg",
    "headroom",
    "is_upswitch",
    "is_downswitch",
    "switch_magnitude",
    "phase_raw",
    "phase_smooth",
    "policy_name",
    "policy_target_rate",
    "policy_chosen_level",
    "policy_decision_ms",
    "eval_phase",
    "is_preroll",
    "use_for_eval",
]

SEGMENT_TELEMETRY_STALL_COLUMNS = [
    "stall_flag",
    "stall_duration",
]

EVALUATION_SEGMENTS_COLUMNS = [
    "segment_index",
    "is_init",
    "eval_phase",
    "use_for_eval",
    "last_fragment_size",
    "last_download_time",
    "fragment_duration",
]

DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS = CURRENT_FEEDBACK_KEYS


def feedback_column_name(feedback_key: object) -> str:
    return "feedback_{0}".format(feedback_key)


def feedback_column_names(feedback_keys: Iterable[object]) -> List[str]:
    return [feedback_column_name(key) for key in feedback_keys]


def build_segment_telemetry_header(feedback_keys: Iterable[object]) -> List[str]:
    header = (
        list(SEGMENT_TELEMETRY_ROW_COLUMNS)
        + feedback_column_names(feedback_keys)
        + list(SEGMENT_TELEMETRY_SEGMENT_COLUMNS)
        + list(SEGMENT_TELEMETRY_DERIVED_COLUMNS)
        + list(SEGMENT_TELEMETRY_STALL_COLUMNS)
    )
    validate_unique_columns(header, schema_name=SEGMENT_TELEMETRY_FILENAME)
    return header


def build_default_segment_telemetry_header() -> List[str]:
    return build_segment_telemetry_header(DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS)


def build_evaluation_segments_header() -> List[str]:
    header = list(EVALUATION_SEGMENTS_COLUMNS)
    validate_unique_columns(header, schema_name=EVALUATION_SEGMENTS_FILENAME)
    return header


# Legacy names are retained as import aliases only. New code should use the
# segment telemetry and evaluation segment terminology above.
DATASET_SCHEMA_VERSION = SEGMENT_TELEMETRY_SCHEMA_VERSION
TRAINING_SCHEMA_VERSION = EVALUATION_SEGMENTS_SCHEMA_VERSION
DATASET_ROW_COLUMNS = SEGMENT_TELEMETRY_ROW_COLUMNS
DATASET_SEGMENT_COLUMNS = SEGMENT_TELEMETRY_SEGMENT_COLUMNS
DATASET_DERIVED_COLUMNS = SEGMENT_TELEMETRY_DERIVED_COLUMNS
DATASET_STALL_COLUMNS = SEGMENT_TELEMETRY_STALL_COLUMNS
TRAINING_COLUMNS = EVALUATION_SEGMENTS_COLUMNS
build_dataset_header = build_segment_telemetry_header
build_training_header = build_evaluation_segments_header


def validate_unique_columns(columns: Sequence[str], schema_name: str = "CSV schema") -> None:
    counts = Counter(columns)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        raise RuntimeError(
            "{0} has duplicate column names: {1}".format(
                schema_name,
                ", ".join(duplicates),
            )
        )


def validate_row_length(row: Sequence[object], header: Sequence[str], schema_name: str = "CSV row") -> None:
    if len(row) != len(header):
        raise RuntimeError(
            "{0} length mismatch: row has {1} values but header has {2} columns".format(
                schema_name,
                len(row),
                len(header),
            )
        )
