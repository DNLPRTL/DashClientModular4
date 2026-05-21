# Common Trace Schema

This document defines `normalized_trace_schema_v1`, the common internal trace format for Phase 3 trace/replay work.

Phase 3.2B is documentation-only. It does not implement a runner, converters, dataset downloads, QoE/reward, IA/RL, controller changes, player changes, media-engine changes or metric-definition changes.

## Schema Decision

The normalized trace schema is a CSV-like time series. Each row represents an interval of available/application-level downlink throughput.

Required columns:

| column | type | required | semantics |
| --- | --- | --- | --- |
| `timestamp_s` | number | yes | Seconds from trace start. Must be numeric and monotonically non-decreasing. |
| `duration_s` | number | yes | Duration represented by the sample. Must be numeric and positive. |
| `throughput_kbps` | number | yes | Available/application-level downlink throughput for the interval. Must be numeric and greater than or equal to 0. |

Optional columns:

| column | type | required by Phase 3 runner | semantics |
| --- | --- | --- | --- |
| `rtt_ms` | number | no | Round-trip time in milliseconds if the source provides it. |
| `jitter_ms` | number | no | Jitter in milliseconds if the source provides it. |
| `loss_rate` | number | no | Packet or delivery loss ratio in `[0, 1]` if the source provides it. |
| `source_timestamp` | string/number | no | Original source timestamp before normalization. |
| `latitude` | number | no | Optional location metadata. |
| `longitude` | number | no | Optional location metadata. |
| `mobility_label` | string | no | Optional source or converter mobility label. |
| `network_type` | string | no | Optional normalized network family, for example `HSDPA`, `LTE`, `5G`, `HAS`, `fixed_broadband`. |
| `operator_or_carrier` | string | no | Optional operator/carrier label when available and safe to retain. |
| `scenario_label` | string | no | Optional scenario label assigned by the converter or split policy. |
| `source_dataset` | string | no | Dataset id from the Phase 3 matrix. |
| `source_file` | string | no | Raw source file id or path token, not necessarily a local path. |
| `notes` | string | no | Human-readable conversion notes. |

## Required Semantics

- `timestamp_s` starts at or after `0`.
- `timestamp_s` is seconds from trace start, not wall-clock time.
- `timestamp_s` must be monotonically non-decreasing.
- `duration_s` must be positive.
- `throughput_kbps` is canonical throughput in kilobits per second.
- `throughput_kbps = 0` is allowed and represents outage/no-delivery intervals.
- Missing throughput is not the same as zero throughput. Missing or invalid source values must be rejected or explicitly imputed by a documented converter policy.
- Overlapping or duplicate timestamps require a dataset-specific converter decision before use.

## Controller Isolation

The runner must not expose future trace samples directly to controllers. Controllers see only normal client/controller signals already produced by the player loop, such as buffer, measured download timing, rate ladder and current representation state.

Optional context columns may be preserved for future IA work and analysis, but Phase 2 baseline controllers must not require them.

## Relationship To Future Runner

The likely primary runner remains a custom Python trace-driven fake/replay runner because it is deterministic, testable with `unittest`, compatible with Windows/Ubuntu, and suitable for future IA training loops. This document defines the input contract for that future runner; it does not implement it.

Mahimahi remains a secondary Ubuntu validation candidate. Linux `tc/netem` remains a Linux fallback or runbook candidate. Neither is implemented or selected as the final benchmark path in Phase 3.2B.

## Non-Goals

- no replay implementation;
- no converter implementation;
- no dataset download;
- no final QoE/reward;
- no benchmark ranking;
- no IA/RL;
- no controller/player/runtime/media-engine/metric changes;
- no real trace files in the repository.

