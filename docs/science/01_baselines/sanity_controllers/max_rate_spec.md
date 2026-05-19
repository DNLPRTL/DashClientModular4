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
- Empty, missing or malformed ladders return safe target `0.0` without crashing in the formal controller.
- No throughput, buffer, or QoE signal is required.
- The formal controller name is `max_rate`.
- The implementation module is `core/controller/sanity_rate.py`.
- The target rate is the highest available ladder value in bytes per second, respecting `max_level` when present.

## Non-Goals

- Not an academic baseline.
- Not a recommendation for real playback.
- Not a benchmark result by itself.
