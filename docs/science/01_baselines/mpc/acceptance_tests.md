# mpc Acceptance Tests

These tests specify future small-horizon MPC behavior. They do not add code tests in this block.

## Unit Tests

Use rates `[100, 200, 400]` bytes/s, `segment_duration_s = 4.0`, `horizon = 2`, `quality = ln(rate/min_rate)`, `rebuffer_penalty = 4.3`, and `switch_penalty = 1.0` unless stated otherwise.

| test | input | expected result | tolerance |
| --- | --- | --- | --- |
| harmonic mean predictor | throughput history `[100, 200, 400]` | `171.428571` bytes/s | `1e-6` |
| no history fallback | no valid throughput samples | target `100`, level `0` | exact |
| one-level ladder | rates `[250]` | target `250`, level `0` | exact |
| invalid duration | duration `0` or negative | startup target `100` | exact |
| high throughput and buffer | predicted throughput `1000`, buffer `20`, current level `0` | first action level `2` | exact |
| low buffer rebuffer avoidance | predicted throughput `180`, buffer `1`, current level `2` | first action level `0` | exact |
| switch penalty applies | same score except one sequence switches more | lower-switch sequence wins | exact tie-break by score |
| first action only | best sequence `[1, 2]` | target is level `1`, not level `2` | exact |
| sequence limit | ladder and horizon exceed `max_enumerated_sequences` | horizon reduced or config failure, never silent explosion | exact |
| invalid throughput samples | history includes zero/negative samples | ignored in predictor | exact |

## Fake Smoke Tests

| scenario | setup | expected result | what it proves |
| --- | --- | --- | --- |
| stable high capacity | fake feedback produces high positive throughput and healthy buffer | controller selects higher levels after history exists | planner uses throughput and buffer |
| unstable low capacity | fake feedback produces low throughput and low buffer | controller selects low level | rebuffer avoidance |
| startup | first decisions have insufficient history | startup/min level | safe fallback |
| switch penalty | alternating conditions with same throughput | fewer unnecessary switches than no-penalty fixture | switching term active |

Smoke outputs are not benchmark results.

## Minimum Scenarios

- Empty ladder validation failure.
- Single-level ladder.
- No throughput history.
- Missing buffer.
- Invalid segment duration.
- Horizon larger than tractable sequence count.

## Invariants

- Uses both throughput prediction and buffer simulation.
- Returns target rate in bytes per second.
- Uses only the first action of the best sequence.
- Internal objective is not final QoE.
- Deterministic for identical feedback and history.

## Invalidating Failures

- Using future throughput oracle values.
- Using external solvers in the first implementation.
- Returning a later action from the best sequence instead of the first.
- Writing final metric definitions or benchmark scores.
- Modifying runtime/player/metric/config files.
- Claiming fake smoke output as benchmark evidence.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These tests validate the controller's internal planning behavior only. They do not define final QoE, benchmark reward, trace replay, emulation, or comparative scientific results.
