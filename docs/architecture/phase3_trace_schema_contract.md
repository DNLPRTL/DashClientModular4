# Phase 3 Trace Schema Contract

This architecture contract records the Phase 3.2B trace schema boundary for DashClientModular4.

## Contract

Future trace/replay work must use `normalized_trace_schema_v1` as the internal trace input contract.

Required normalized trace columns:

| column | unit | rule |
| --- | --- | --- |
| `timestamp_s` | seconds | Numeric seconds from trace start; monotonically non-decreasing. |
| `duration_s` | seconds | Numeric interval duration; strictly positive. |
| `throughput_kbps` | kilobits per second | Numeric available/application-level downlink throughput; greater than or equal to 0. |

Optional context columns may be preserved, but Phase 2 baseline controllers must not require them.

## Runtime Boundary

The future runner must not expose future trace samples directly to controllers. Controllers may only receive normal client/controller signals produced by the playback loop.

This contract does not authorize:

- replay implementation;
- converter implementation;
- dataset download;
- QoE/reward definition;
- benchmark ranking;
- IA/RL implementation;
- controller changes;
- player/runtime changes;
- media-engine changes;
- metric-definition changes.

## Storage Boundary

Raw datasets, normalized traces and generated manifests must stay outside the repository:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_normalized\schema_v1
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_manifests
```

The repository contains authored documentation and may contain future tiny synthetic fixtures only if a later implementation block explicitly authorizes them.

## Method Boundary

The likely primary runner is a custom Python trace-driven fake/replay runner because it can be deterministic, tested with `unittest`, compatible with Windows/Ubuntu, and usable in future IA training loops.

Mahimahi is a secondary Ubuntu validation candidate. Linux `tc/netem` is a Linux fallback/runbook candidate. Neither is implemented or selected as the final benchmark path by this contract.

