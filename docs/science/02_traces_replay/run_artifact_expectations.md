# Run Artifact Expectations

This document defines expected future artifacts. Phase 3.1 creates none of them.

## Future Artifact Types

| artifact | purpose | git policy |
| --- | --- | --- |
| run manifest | Record commit, controller, trace, split, config and method. | Generated; do not commit unless manually summarized. |
| normalized trace copy | Immutable input used for a run. | Keep outside repo. |
| telemetry CSV | Per-segment or per-event measurements. | Keep outside repo. |
| summary JSON/CSV | Aggregated run metrics. | Keep outside repo until final policy exists. |
| plots | Visual summaries. | Generated; do not commit without explicit thesis figure decision. |
| logs | Debug/runtime output. | Keep outside repo. |
| environment snapshot | Python version, OS, dependency info. | Generated; summarize manually if needed. |

## Required Manifest Fields

Future run manifests should include:

- repository commit;
- controller name;
- runner/emulator method;
- dataset ID;
- trace ID;
- split;
- trace version or checksum;
- config file path or digest;
- random seed if any;
- output directory;
- timestamp;
- metric definition version once metrics are finalized.

## Repository Hygiene

Do not commit:

- raw datasets;
- PDFs;
- generated logs;
- generated CSV files;
- ZIP archives;
- media files;
- benchmark run directories;
- `.venv`, `.idea`, `__pycache__`, `.pyc`.

Manual Markdown summaries may be committed later only when they are authored documentation, not raw generated artifacts.

## Phase 3.2A Source-Triage Update

Future trace/replay runs must include at least:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `run.log`
- `segment_telemetry.csv`
- `evaluation_segments.csv`
- `trace_manifest.json` or equivalent trace provenance artifact
- `split_manifest.json` or embedded split metadata

No Phase 3.2A work creates these artifacts.

## Phase 3.2B Schema Update

Future trace/replay artifacts must include schema provenance:

- normalized traces follow `normalized_trace_schema_v1`;
- trace provenance follows `trace_manifest_v1`;
- split provenance follows `split_manifest_v1`;
- run manifests should include trace id, dataset id, converter version/commit, checksum and split label.

Raw traces, normalized real traces and generated manifests remain outside the repository unless a later block explicitly converts a tiny synthetic fixture for tests.

## Phase 3.2C Local Acquisition Update

The local raw acquisition audit is not a run artifact and not a benchmark artifact.

Do not commit:

- local JSON inventories;
- raw logs;
- ZIP archives;
- normalized trace files;
- generated manifests;
- benchmark telemetry;
- plots or run summaries produced by tools.

Authored Markdown summaries such as `phase3_2c_dataset_audit_summary.md` are allowed.
