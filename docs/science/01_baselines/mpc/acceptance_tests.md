# mpc Acceptance Tests

These tests specify and validate the implemented small-horizon MPC behavior. They do not define final QoE, benchmark reward, replay traces, or comparative results.

## Unit Tests

Implemented in `tests/test_mpc_controller.py`. Default test ladder uses `[100, 200, 400]` bytes/s, `segment_duration_s = 4.0`, `quality = ln(rate/min_rate)`, `rebuffer_penalty = 4.3`, and `switch_penalty = 1.0` unless a test overrides parameters.

| test | input | expected result | status |
| --- | --- | --- | --- |
| registry entry | controller registry | `mpc` is registered and creatable | implemented |
| existing controllers | registry keys | `min_rate`, `fixed_rate`, `max_rate`, `rate_based`, `bba`, `bola`, `fixed_quality`, `scripted_quality`, `max_quality` remain registered | implemented |
| dict API contract | `setPlayerFeedback`, `calcControlAction`, `getControlAction`, `quantizeRate` | target rate in bytes/s and quality index from ladder | implemented |
| no console dependency | redirected stdout | decision is unchanged and no stdout is required | implemented |
| harmonic mean predictor | throughput history `[100, 200, 400]` plus invalid samples in separate test | `171.428571` bytes/s over positive samples | implemented |
| no history fallback | no valid throughput samples | target minimum/startup level | implemented |
| one-level ladder | rates `[250]` | target `250`, level `0` | implemented |
| invalid duration | duration `0` or invalid | startup target | implemented |
| high throughput and buffer | predicted throughput high, healthy buffer | higher quality allowed | implemented |
| low throughput | predicted throughput too low for high level | lower quality selected | implemented |
| rebuffer penalty applies | same ladder with different rebuffer penalty | high penalty avoids rebuffer-heavy option | implemented |
| switch penalty applies | same ladder with different switch penalty | high penalty avoids unnecessary jump | implemented |
| first action only | best sequence starts below its later action | returned target is first level of sequence | implemented |
| segment-size approximation | no exact size list | `rate * fragment_duration` sizes used | implemented |
| exact segment sizes | exact per-level sizes supplied | exact sizes used in simulated download time | implemented |
| invalid/missing buffer | invalid buffer fields | simulation starts from `0` seconds | implemented |
| unit conversion | rates in bits/s | normalized to bytes/s target | implemented |
| invalid parameters | bad horizon, penalties, enum, throughput floor | safe defaults used | implemented |
| deterministic behavior | identical input and controller state | identical decision and metrics | implemented |
| sequence limit | ladder/horizon exceeds limit | effective horizon reduced, no combinatorial explosion | implemented |
| forbidden signals | RTT/loss/cwnd/server/future/QoE/RL/log fields | decision unchanged | implemented |

## Fake Smoke Tests

| scenario | setup | expected result | what it proves | status |
| --- | --- | --- | --- | --- |
| standard stable fake run | short fake-engine CLI run with `controller.name = "mpc"` | canonical artifacts exist and strict readiness still passes | controller integrates through existing runtime contract | required for Phase 2.3.5 |
| low-capacity fake run | controlled low-capacity fixture | would exercise lower-quality adaptation under constrained throughput | richer runtime scenario support | deferred until replay/traces or a controlled fake capacity fixture exists |

Smoke outputs are not benchmark results. They validate implementation and integration only.

## Minimum Scenarios

- Empty ladder safe fallback.
- Single-level ladder.
- No throughput history.
- Missing/invalid buffer.
- Invalid segment duration.
- Horizon larger than tractable sequence count.

## Invariants

- Uses both throughput prediction and buffer simulation.
- Returns target rate in bytes per second.
- Uses only the first action of the best sequence.
- Internal objective is not final QoE.
- Deterministic for identical feedback and history.
- Does not use future throughput oracle, TCP internals, console output, final QoE/reward, or RL state.

## Invalidating Failures

- Using future throughput oracle values.
- Using external solvers in the first implementation.
- Returning a later action from the best sequence instead of the first.
- Writing final metric definitions or benchmark scores.
- Modifying runtime/player/media-engine/metric files.
- Claiming fake smoke output as benchmark evidence.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Windows | requested controller `py_compile` commands | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These tests validate the controller's internal planning behavior only. They do not define final QoE, benchmark reward, trace replay, emulation, or comparative scientific results.
