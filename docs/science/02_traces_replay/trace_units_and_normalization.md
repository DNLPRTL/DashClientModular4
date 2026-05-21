# Trace Units And Normalization

This document defines the unit policy for `normalized_trace_schema_v1`.

## Canonical Units

| quantity | canonical unit | field |
| --- | --- | --- |
| throughput | kilobits per second | `throughput_kbps` |
| time | seconds | `timestamp_s`, `duration_s` |
| RTT | milliseconds | `rtt_ms` |
| jitter | milliseconds | `jitter_ms` |
| loss | ratio in `[0, 1]` | `loss_rate` |
| latitude/longitude | decimal degrees | `latitude`, `longitude` |

## Throughput Conversion Policy

All input throughput units must be converted to `throughput_kbps`.

| source unit | conversion to `throughput_kbps` |
| --- | --- |
| `kbps` | keep as-is after numeric validation |
| `Mbps` or `Mbit/s` | `value * 1000` |
| `bps` | `value / 1000` |
| `B/s` or bytes per second | `value * 8 / 1000` |
| bytes per sample period | `bytes * 8 / duration_s / 1000` |
| bits per sample period | `bits / duration_s / 1000` |

Dataset-specific converters must record the source unit and formula in the trace manifest notes or converter documentation.

## Time Conversion Policy

- All normalized timestamps are seconds from trace start.
- Wall-clock timestamps must be converted to relative seconds and may be preserved in `source_timestamp`.
- Sample intervals must become positive `duration_s` values.
- If a source provides timestamps but not durations, a converter may infer each row duration from the next timestamp only when this rule is documented.
- The final row duration must use a dataset-specific policy, such as nominal granularity, source duration or rejection if ambiguous.

## Optional Context Policy

Location, mobility, network, carrier and radio KPI context may be preserved when available. These columns are metadata for future analysis or IA work. They are not required by the Phase 3 runner and must not be required by Phase 2 baseline controllers.

## Validation Rules

Every normalized trace must satisfy:

1. required columns exist;
2. `timestamp_s`, `duration_s` and `throughput_kbps` parse as numbers;
3. `timestamp_s` is monotonically non-decreasing;
4. every `duration_s` is greater than 0;
5. every `throughput_kbps` is greater than or equal to 0;
6. `loss_rate`, if present, is between 0 and 1;
7. optional numeric columns either parse as numbers or are blank under an explicit missing-value policy.

## Forbidden Normalization Shortcuts

- Do not silently treat missing throughput as 0.
- Do not infer future bandwidth from later samples and expose it to controllers.
- Do not use optional context fields as baseline-controller inputs.
- Do not define final QoE/reward while normalizing traces.
- Do not commit normalized real traces to the repository.

