# Trace Split Manifest Policy

This document defines `split_manifest_v1`. No final split is closed in Phase 3.2B.

## Purpose

The split manifest prevents leakage between train, validation, test and OOD roles before future IA/RL, tuning or final benchmark work begins.

## Manifest Shape

`split_manifest_v1` is JSON-compatible. It may be stored as a single JSON file or as JSONL entries in a future external manifest directory.

Required top-level fields:

| field | type | semantics |
| --- | --- | --- |
| `schema_version` | string | Must be `split_manifest_v1`. |
| `split_manifest_id` | string | Stable id for the split plan. |
| `created_at` | string | Creation timestamp when generated later. |
| `policy_version` | string | Split policy version. |
| `repository_commit` | string | Commit used when the split is produced. |
| `trace_schema_version` | string | Must match `normalized_trace_schema_v1` for real trace inputs. |
| `entries` | array | One entry per trace. |
| `notes` | string | Human-readable limitations and open decisions. |

Required entry fields:

| field | type | semantics |
| --- | --- | --- |
| `trace_id` | string | Trace id from `trace_manifest_v1`. |
| `dataset_id` | string | Dataset id. |
| `split_label` | string | `train`, `validation`, `test`, `OOD`, `synthetic`, `reference_only` or `metadata_only`. |
| `leakage_group` | string | Route/session/day/operator/app/trajectory group. |
| `source_file` | string | Original source file id or token. |
| `domain_label` | string | Domain such as `legacy_mobile`, `LTE`, `live_HAS`, `5G`, `mmWave`, `fixed_reference`. |
| `reason` | string | Why this trace was assigned to the split. |

## Rules

- A `trace_id` must not appear in more than one split.
- Dataset-level and route/session-level leakage must be prevented.
- Windows from the same original trace must not cross split boundaries.
- Repeated routes, sessions, service/day groups, operator/device/app groups and trajectories must stay in one split group unless a dataset card explicitly proves independence.
- For future IA, train/validation/test/OOD must be separated before training starts.
- OOD candidates must include modern mobile/5G traces such as Raca 5G and Lumos5G.
- HSDPA/Ghent/Lancaster are first integration candidates, not final benchmark material by default.
- FCC and Puffer remain `reference_only` or `metadata_only` until separate plans authorize conversion.

## Phase 3.2B Boundary

This document defines only the schema and policy. It does not create a split file, close a final split, download traces, train IA models or run benchmarks.

