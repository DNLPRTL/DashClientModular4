# robust_mpc Acceptance Tests

These tests specify future RobustMPC behavior. They do not add code tests in this block.

## Unit Tests

Use the same MPC objective fixture as `../mpc/acceptance_tests.md`, with `throughput_history_window = 5`, `prediction_error_window = 5`, `startup_safety_factor = 0.85`, and `epsilon_throughput_Bps = 0.001` unless stated otherwise.

| test | input | expected result | tolerance |
| --- | --- | --- | --- |
| zero error correction | base prediction `400`, recent predicted/actual pairs all equal | robust prediction `400` | `1e-9` |
| high error correction | base prediction `400`, max recent error `1.0` | robust prediction `200` | `1e-9` |
| fractional error correction | base prediction `300`, max recent error `0.5` | robust prediction `200` | `1e-9` |
| insufficient prediction history | base prediction `400`, no previous prediction pairs | robust prediction `340` | `1e-9` |
| zero actual throughput guard | predicted `100`, actual `0`, epsilon `0.001` | no division by zero; error finite or sample ignored by spec | exact behavior documented |
| behaves like MPC when error zero | same feedback as MPC and `err = 0` | same first action as MPC | exact |
| more conservative than MPC under high error | same feedback as MPC and high error | chosen level is less than or equal to MPC level | exact |
| one-level ladder | rates `[250]` | target `250`, level `0` | exact |
| no actual throughput | no valid throughput samples | startup/min representation | exact |
| stores prediction | after decision | prediction available for next error calculation | exact |

## Fake Smoke Tests

| scenario | setup | expected result | what it proves |
| --- | --- | --- | --- |
| stable prediction | fake feedback where predicted and actual throughput match | behavior matches MPC | robust layer is neutral when no error |
| recent overprediction | fake feedback where previous predictions exceed actual throughput | robust controller selects lower or equal level than MPC fixture | conservative correction |
| insufficient history | first decisions before prediction pairs exist | startup safety factor path | safe startup |
| no Pensieve artifacts | run without models, traces, or RL state | controller still works | Pensieve is not implemented |

Smoke outputs are not benchmark results.

## Minimum Scenarios

- Empty ladder validation failure.
- Single-level ladder.
- No throughput history.
- No prediction-error history.
- High prediction error.
- Invalid actual throughput.
- Invalid buffer or segment duration.

## Invariants

- Same MPC enumeration structure after robust throughput correction.
- Robust prediction never uses future throughput.
- No Pensieve model, neural inference, RL training, ABR server, traces, or datasets.
- Target rate unit is bytes per second.
- Internal objective is not final QoE.

## Invalidating Failures

- Implementing Pensieve or any neural/RL component.
- Computing error from future observations.
- Allowing high recent overprediction to make the controller less conservative.
- Returning bits per second instead of bytes per second.
- Modifying runtime/player/metric/config files.
- Claiming fake smoke output as benchmark evidence.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These tests validate robust-prediction behavior only. They do not define final QoE, Pensieve comparison results, replay methodology, emulation, or benchmark performance.
