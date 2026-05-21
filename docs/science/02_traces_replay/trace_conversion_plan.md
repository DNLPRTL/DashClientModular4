# Trace Conversion Plan

This document defines the Phase 3 conversion plan. It does not implement converters and does not download datasets.

## Conversion Goal

Every usable external trace source must be converted into `normalized_trace_schema_v1` before a future runner sees it.

The runner must consume the normalized schema, not raw dataset-specific files. This keeps dataset quirks out of controllers, player code, media engines and metric definitions.

## Conversion Priority

First real integration candidates:

1. HSDPA Norway / Riiser MMSys 2013
2. Ghent 4G/LTE Bandwidth Logs
3. Lancaster ABR-Throughput-Traces

Modern/OOD candidates:

4. Raca 4G LTE channel/context
5. Raca 5G channel/context
6. Lumos5G

Reference-only / metadata-only:

7. FCC MBA: reference-only, no raw download yet.
8. Puffer archive: metadata-only, no raw daily download yet.

## Generic Conversion Stages

1. Confirm dataset card and license/terms.
2. Download raw data outside the repository only when a later block authorizes it.
3. Record raw provenance and source file ids.
4. Parse raw samples with a dataset-specific converter.
5. Normalize time to `timestamp_s` and `duration_s`.
6. Normalize throughput to `throughput_kbps`.
7. Preserve optional context fields without making them runner requirements.
8. Validate schema rules.
9. Write normalized traces outside the repository.
10. Write `trace_manifest_v1` outside the repository.
11. Assign split candidates through `split_manifest_v1` policy.

## Implementation Readiness Gate

Replay implementation is not authorized until these docs are closed:

- `common_trace_schema.md`
- `trace_manifest_schema.md`
- `trace_conversion_plan.md`
- `trace_split_manifest_policy.md`
- `trace_schema_acceptance_tests.md`

Converter implementation is also not authorized by this document. A later implementation block must specify the write paths, tests and fixture policy.

## Dataset-Specific Conversion Notes

| dataset | initial conversion direction |
| --- | --- |
| HSDPA Norway | Convert plain ASCII throughput logs to `timestamp_s`, inferred `duration_s` and `throughput_kbps`; preserve route/trace leakage group. |
| Ghent 4G/LTE | Convert log intervals to normalized time and throughput; preserve mobility/mode labels where available. |
| Lancaster HAS | Convert throughput traces already reported in kbps where confirmed; group by service/day/source trace. |
| Raca 4G | Convert throughput column first; preserve channel/context KPIs as optional metadata only. |
| Raca 5G | Convert DL bitrate fields to `throughput_kbps`; preserve app, operator/device and KPI context for leakage grouping. |
| Lumos5G | Convert throughput samples to `throughput_kbps`; protect repeated trajectory/location groups. |
| FCC MBA | Do not convert until a raw-download and derived-throughput plan exists. |
| Puffer archive | Do not convert until storage, schema and causal plans distinguish achieved throughput logs from exogenous capacity traces. |

