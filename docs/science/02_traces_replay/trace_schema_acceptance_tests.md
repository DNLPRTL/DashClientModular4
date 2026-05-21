# Trace Schema Acceptance Tests

This document defines future acceptance tests for `normalized_trace_schema_v1`. It does not add tests or implement validators in Phase 3.2B.

Future tests must use `unittest`, not `pytest`.

## Required Acceptance Areas

| area | future assertion |
| --- | --- |
| required columns | A valid trace includes `timestamp_s`, `duration_s` and `throughput_kbps`. |
| numeric parsing | Required columns parse as numbers. |
| timestamp order | `timestamp_s` is monotonically non-decreasing. |
| positive duration | Every `duration_s` is greater than 0. |
| throughput range | Every `throughput_kbps` is greater than or equal to 0. |
| outage support | `throughput_kbps = 0` is accepted as an outage/no-delivery interval. |
| invalid missing throughput | Missing throughput is rejected unless a converter policy explicitly handles it before normalization. |
| optional columns | Optional context columns are accepted but not required. |
| controller isolation | Runner tests must prove controllers do not receive future samples or optional context fields directly. |
| manifest consistency | Trace manifest statistics match the normalized file. |

## Minimal Synthetic Test Fixtures

Future implementation may define tiny synthetic fixtures only if explicitly authorized by a later block.

Required shapes:

- `constant_high`
- `constant_low`
- `step_down`
- `step_up`
- `oscillating`
- `zero_gap`
- invalid negative throughput;
- invalid zero or negative duration;
- invalid decreasing timestamp.

Synthetic traces are schema and runner fixtures only. They are not benchmark evidence and do not define final QoE/reward.

## Implementation Gate

Replay implementation should not begin until future tests cover:

1. schema validation;
2. unit conversion;
3. manifest consistency;
4. split manifest uniqueness;
5. no future-sample exposure to controllers;
6. no optional context dependency for Phase 2 baselines.

