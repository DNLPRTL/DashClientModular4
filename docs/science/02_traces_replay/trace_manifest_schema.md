# Trace Manifest Schema

This document defines `trace_manifest_v1`, a JSON or JSONL-compatible metadata schema for normalized traces.

Phase 3.2B documents the schema only. It creates no manifest files and downloads no data.

## Required Fields

| field | type | required | semantics |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Must identify the manifest schema, for example `trace_manifest_v1`. |
| `trace_id` | string | yes | Stable id for one normalized trace. |
| `dataset_id` | string | yes | Dataset id from `trace_dataset_matrix.md`. |
| `dataset_card_path` | string | yes | Repository path to the dataset/source card. |
| `source_name` | string | yes | Human-readable source name. |
| `source_url_or_reference` | string | yes | URL, DOI, repository or source reference. |
| `license` | string | yes | License or usage terms, or `Unknown/TBD`. |
| `download_date` | string/null | yes | Date of external raw download, or null when not downloaded. |
| `raw_local_path_policy` | string | yes | Policy for raw storage location outside the repo. |
| `normalized_local_path_policy` | string | yes | Policy for normalized storage location outside the repo. |
| `converter_name` | string | yes | Converter identifier, even if future/TBD. |
| `converter_version_or_commit` | string | yes | Converter version, repository commit or `TBD`. |
| `checksum_sha256` | string | yes | SHA-256 checksum of the normalized trace file, or `TBD` before generation. |
| `sample_count` | integer | yes | Number of normalized rows. |
| `duration_s` | number | yes | Total represented duration in seconds. |
| `nominal_granularity_s` | number/string | yes | Expected sample interval or `mixed`. |
| `throughput_unit` | string | yes | Must be `kbps` for normalized traces. |
| `min_throughput_kbps` | number | yes | Minimum normalized throughput. |
| `mean_throughput_kbps` | number | yes | Mean normalized throughput. |
| `max_throughput_kbps` | number | yes | Maximum normalized throughput. |
| `scenario_tags` | array of strings | yes | Scenario labels such as `constant`, `mobile`, `live_has`, `outage`, `variable`. |
| `mobility_tags` | array of strings | yes | Mobility labels such as `stationary`, `pedestrian`, `vehicle`, `route`, `unknown`. |
| `network_tags` | array of strings | yes | Network labels such as `HSDPA`, `LTE`, `5G`, `mmWave`, `HAS`, `fixed_broadband`. |
| `split_candidate` | string | yes | Candidate split role: `train`, `validation`, `test`, `OOD`, `synthetic`, `reference_only`, `metadata_only`, or `not_final`. |
| `leakage_group` | string | yes | Group id used to prevent route/session/day/source leakage across splits. |
| `notes` | string | yes | Human-readable notes, uncertainty and limitations. |

## Manifest Rules

- A manifest describes exactly one normalized trace file.
- `trace_id` must be unique within the local manifest collection.
- `dataset_card_path` must point to an authored Markdown card in `docs/science/02_traces_replay/trace_dataset_cards/`.
- `throughput_unit` must be `kbps`.
- `checksum_sha256` is required before any benchmark-grade run can reference the trace.
- `download_date` must remain null for reference-only or metadata-only sources.
- `raw_local_path_policy` and `normalized_local_path_policy` are policies or external paths, not committed data.

## Example Shape

This example is illustrative schema prose, not a generated artifact:

```json
{
  "schema_version": "trace_manifest_v1",
  "trace_id": "example_dataset_trace_001",
  "dataset_id": "example_dataset",
  "dataset_card_path": "docs/science/02_traces_replay/trace_dataset_cards/example.md",
  "source_name": "Example source",
  "source_url_or_reference": "TBD",
  "license": "Unknown/TBD",
  "download_date": null,
  "raw_local_path_policy": "outside repo",
  "normalized_local_path_policy": "outside repo",
  "converter_name": "TBD",
  "converter_version_or_commit": "TBD",
  "checksum_sha256": "TBD",
  "sample_count": 0,
  "duration_s": 0,
  "nominal_granularity_s": "TBD",
  "throughput_unit": "kbps",
  "min_throughput_kbps": 0,
  "mean_throughput_kbps": 0,
  "max_throughput_kbps": 0,
  "scenario_tags": [],
  "mobility_tags": [],
  "network_tags": [],
  "split_candidate": "not_final",
  "leakage_group": "TBD",
  "notes": "Schema example only."
}
```

