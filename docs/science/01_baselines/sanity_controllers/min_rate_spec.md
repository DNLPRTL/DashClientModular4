# Min-Rate Sanity Controller Spec

## Purpose

`min_rate` is a sanity controller that always targets the lowest representation rate available in the MPD ladder.

## Behavior

| item | value |
| --- | --- |
| input | `rates` / `min_rate` |
| output | minimum representation rate in bytes per second |
| selection | quantizes to the lowest representation |
| state | no adaptive state |
| QoE claim | none |

## Invariants

- One-level ladders select level 0.
- Empty or invalid ladders must fail through the shared contract validation.
- No throughput, buffer, or QoE signal is required.

## Non-Goals

- Not an academic baseline.
- Not a low-quality QoE recommendation.
- Not a benchmark result by itself.
