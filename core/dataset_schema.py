from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Sequence


DATASET_SCHEMA_VERSION = "1.1"
TRAINING_SCHEMA_VERSION = "1.1"

DATASET_ROW_COLUMNS = [
    "segment_index",
    "timestamp",
]

DATASET_SEGMENT_COLUMNS = [
    "is_init",
    "retry_count",
    "segment_start_time",
    "segment_end_time",
    "wall_time_elapsed",
]

DATASET_DERIVED_COLUMNS = [
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

DATASET_STALL_COLUMNS = [
    "stall_flag",
    "stall_duration",
]

TRAINING_COLUMNS = [
    "segment_index",
    "is_init",
    "eval_phase",
    "use_for_eval",
    "last_fragment_size",
    "last_download_time",
    "fragment_duration",
]


def feedback_column_name(feedback_key: object) -> str:
    return "feedback_{0}".format(feedback_key)


def feedback_column_names(feedback_keys: Iterable[object]) -> List[str]:
    return [feedback_column_name(key) for key in feedback_keys]


def build_dataset_header(feedback_keys: Iterable[object]) -> List[str]:
    header = (
        list(DATASET_ROW_COLUMNS)
        + feedback_column_names(feedback_keys)
        + list(DATASET_SEGMENT_COLUMNS)
        + list(DATASET_DERIVED_COLUMNS)
        + list(DATASET_STALL_COLUMNS)
    )
    validate_unique_columns(header, schema_name="dataset.csv")
    return header


def build_training_header() -> List[str]:
    header = list(TRAINING_COLUMNS)
    validate_unique_columns(header, schema_name="dataset_training.csv")
    return header


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
