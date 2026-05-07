# Hardening Step 6: Dataset Telemetry Schema Contract

Date: 2026-05-07

This step makes the generated CSV headers explicit, deterministic, and test-protected.

## What Changed

- Added `core/dataset_schema.py`.
- Added `tests/test_dataset_schema.py`.
- Updated `player.py` to build CSV headers through the schema helper.
- Extended the offline fake-engine smoke test to assert unique headers and row/header length alignment.

## Dataset Files

`dataset.csv` is the full telemetry CSV for a validation run. It keeps the existing row values and ordering, but feedback-derived column names now use the `feedback_` prefix.

Examples:

- `queued_bytes` becomes `feedback_queued_bytes`
- `queued_time` becomes `feedback_queued_time`
- `segment_index` becomes `feedback_segment_index`
- `start_segment_request` becomes `feedback_start_segment_request`

The top-level row column `segment_index` remains unchanged. This removes ambiguity between row metadata and feedback-derived telemetry without changing numerical values or row semantics.

`dataset_training.csv` remains the minimal training-oriented CSV. Its filename, path, row values, and units are unchanged in this block.

## Contract

- `dataset.csv` column names must be unique.
- `dataset_training.csv` column names must be unique.
- Data row lengths must match their headers.
- Duplicate column names raise a clear `RuntimeError` before writing the header.

## Boundaries Preserved

- No ABR algorithms were added.
- Controller APIs were not redesigned.
- Downloader, parser, buffering, retry behavior, warm-up, preroll, pacing, downshift behavior, stall handling, throughput estimation, GStreamer timing, QoE logic, and ABR decisions were not changed.
- Units were not changed.
- Output files remain `dataset.csv` and `dataset_training.csv`.
- Output paths are unchanged.
- GStreamer remains optional on Windows.

## Current Caveats

Generated datasets are still validation artifacts, not final benchmark results.

The GStreamer runtime path is still operational validation only and is not benchmark-grade yet.

Baseline ABR algorithms and final QoE/benchmark comparisons remain pending.
