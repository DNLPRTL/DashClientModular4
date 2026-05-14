# Max-Rate Sanity Controller Spec

## Purpose

`max_rate` is a sanity controller that always targets the highest representation rate available in the MPD ladder.

## Behavior

| item | value |
| --- | --- |
| input | `rates` / `max_rate` |
| output | maximum representation rate in bytes per second |
| selection | quantizes to the highest representation |
| state | no adaptive state |
| QoE claim | none |

## Invariants

- One-level ladders select level 0.
- Empty or invalid ladders must fail through the shared contract validation.
- No throughput, buffer, or QoE signal is required.

## Non-Goals

- Not an academic baseline.
- Not a recommendation for real playback.
- Not a benchmark result by itself.
