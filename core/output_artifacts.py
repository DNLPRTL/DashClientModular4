from __future__ import annotations

RUN_MANIFEST_FILENAME = "run_manifest.json"
RESOLVED_CONFIG_FILENAME = "config.resolved.json"
ENVIRONMENT_FILENAME = "environment.json"
RUN_LOG_FILENAME = "run.log"
SEGMENT_TELEMETRY_FILENAME = "segment_telemetry.csv"
EVALUATION_SEGMENTS_FILENAME = "evaluation_segments.csv"

RUN_MANIFEST_KEY = "run_manifest"
RESOLVED_CONFIG_KEY = "resolved_config"
ENVIRONMENT_KEY = "environment"
RUN_LOG_KEY = "run_log"
SEGMENT_TELEMETRY_KEY = "segment_telemetry"
EVALUATION_SEGMENTS_KEY = "evaluation_segments"

LEGACY_OUTPUT_FILENAMES = (
    "dataset.csv",
    "dataset_training.csv",
)

CANONICAL_OUTPUT_KEYS = (
    RUN_MANIFEST_KEY,
    RESOLVED_CONFIG_KEY,
    ENVIRONMENT_KEY,
    SEGMENT_TELEMETRY_KEY,
    EVALUATION_SEGMENTS_KEY,
    RUN_LOG_KEY,
)
