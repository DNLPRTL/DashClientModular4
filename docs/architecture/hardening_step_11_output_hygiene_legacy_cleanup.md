# Hardening Step 11: Output Hygiene And Legacy Cleanup

This block exists to avoid dragging legacy/prototype naming into the academic client. The runtime artifacts should be easy to explain, defend, and test before real ABR baselines or IA work are added.

## What Changed

- Added canonical output artifact constants in `core/output_artifacts.py`.
- Renamed new run outputs from `dataset.csv` to `segment_telemetry.csv`.
- Renamed new compact outputs from `dataset_training.csv` to `evaluation_segments.csv`.
- Updated `run_manifest.json` to use canonical output keys: `run_manifest`, `resolved_config`, `environment`, `segment_telemetry`, `evaluation_segments`, and `run_log`.
- Added benchmark-neutrality metadata to the manifest.
- Updated config, run context, CSV schema helpers, player output messages, tests, README, runbooks, and current architecture docs.

## Why

`dataset_training.csv` was misleading because no final training pipeline exists. It suggested a finished IA dataset before the client has final benchmark methodology, final QoE/reward, academic baselines, or trace infrastructure.

The new names make the current intent explicit:

- `segment_telemetry.csv`: full per-segment/runtime telemetry.
- `evaluation_segments.csv`: compact evaluation-oriented segment records, not final IA training data.

Old names are deprecated and should not be produced by new runs.

## Non-Goals

No playback semantics were changed. No benchmark/QoE/reward finalization was performed. No baselines or AI were implemented. GStreamer was not hardened in this block.

Downloader behavior, parser behavior, media-engine behavior, buffering, pacing, drain mechanics, retry behavior, controller decisions, and GStreamer timing were intentionally left unchanged.

Generated CSVs remain validation/control artifacts. Rows with `use_for_eval=false` are not benchmark rows, terminal drain stalls are not steady-state rebuffering, and fake-engine outputs must not be mixed with GStreamer outputs as equivalent benchmark results.
