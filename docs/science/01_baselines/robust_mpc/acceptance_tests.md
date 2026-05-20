# robust_mpc Acceptance Tests

These tests specify and validate implemented RobustMPC behavior. They do not define final QoE, Pensieve comparison results, replay methodology, emulation, or benchmark performance.

## Unit Tests

Implemented in `tests/test_robust_mpc_controller.py`. Default fixtures reuse the same MPC objective as `../mpc/acceptance_tests.md`, with `throughput_history_window = 5`, `prediction_error_window = 5`, `startup_safety_factor = 0.85`, and `epsilon_throughput_Bps = 0.001` unless a test overrides parameters.

| test | input | expected result | status |
| --- | --- | --- | --- |
| registry entry | controller registry | `robust_mpc` is registered and creatable | implemented |
| existing controllers | registry keys | `min_rate`, `fixed_rate`, `max_rate`, `rate_based`, `bba`, `bola`, `mpc`, `fixed_quality`, `scripted_quality`, `max_quality` remain registered | implemented |
| dict API contract | `setPlayerFeedback`, `calcControlAction`, `getControlAction`, `quantizeRate` | target rate in bytes/s and quality index from ladder | implemented |
| no console dependency | redirected stdout | decision is unchanged and no stdout is required | implemented |
| zero error correction | base prediction `1000`, recent error `0` | robust prediction equals base and decision matches MPC | implemented |
| high error correction | base prediction `350`, max recent error `1.0` | robust prediction `175`; chosen level lower/equal than MPC | implemented |
| fractional error correction | base prediction `400`, max recent error `0.5` | robust prediction `266.666667` | implemented |
| insufficient prediction history | base prediction `400`, no error history | robust prediction `340` using startup safety factor | implemented |
| zero actual throughput guard | explicit actual history includes `0` | no division by zero; invalid actual sample ignored safely | implemented |
| robust prediction bound | positive error | robust prediction is not greater than base prediction | implemented |
| bounded error window | error list longer than window | max is taken from most recent bounded window | implemented |
| stored prediction alignment | two sequential measured samples | previous robust prediction compared with later actual sample | implemented |
| explicit prediction/actual histories | paired histories in feedback | error history derived from pairs | implemented |
| high throughput/high buffer | healthy base prediction and buffer | high quality can be selected | implemented |
| low throughput/low buffer | constrained prediction and low buffer | lower quality selected | implemented |
| first action only | best sequence starts below its later action | returned target is first level of sequence | implemented |
| single-level ladder | rates `[250]` | target `250`, level `0` | implemented |
| invalid ladder | empty/missing/malformed ladder | safe `0.0` fallback | implemented |
| invalid duration/buffer | invalid feedback values | safe fallback or simulation from `0` | implemented |
| invalid params | bad robust/MPC params | documented defaults used | implemented |
| horizon cap | large ladder and horizon | effective horizon reduced | implemented |
| forbidden signals | RTT/loss/server/future/QoE/Pensieve/RL/log fields | decision unchanged | implemented |

## Fake Smoke Tests

| scenario | setup | expected result | what it proves | status |
| --- | --- | --- | --- | --- |
| standard stable fake run | short fake-engine CLI run with `controller.name = "robust_mpc"` | canonical artifacts exist and strict readiness still passes | controller integrates through existing runtime contract | required for Phase 2.3.6 |
| low/unstable capacity fake run | controlled low/unstable capacity fixture | would exercise conservative correction under unstable throughput | richer runtime scenario support | deferred until replay/traces or a controlled fake capacity fixture exists |
| no Pensieve artifacts | run without models, traces, datasets or RL state | controller still works | Pensieve is not implemented | covered by unit invariants and standard smoke |

Smoke outputs are not benchmark results. They validate implementation and integration only.

## Minimum Scenarios

- Empty ladder safe fallback.
- Single-level ladder.
- No throughput history.
- No prediction-error history.
- High prediction error.
- Invalid actual throughput.
- Invalid buffer or segment duration.
- Forbidden Pensieve/RL fields.

## Invariants

- Same MPC enumeration structure after robust throughput correction.
- Robust prediction never uses future throughput.
- No Pensieve model, neural inference, RL training, ABR server, traces, or datasets.
- Target rate unit is bytes per second.
- Quality level is representation index.
- Internal objective is not final QoE.

## Invalidating Failures

- Implementing Pensieve or any neural/RL component.
- Computing error from future observations.
- Allowing high recent overprediction to make the controller less conservative.
- Returning bits per second instead of bytes per second.
- Modifying runtime/player/media-engine/metric/config files.
- Claiming fake smoke output as benchmark evidence.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Windows | requested controller `py_compile` commands | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These tests validate robust-prediction behavior only. They do not define final QoE, Pensieve comparison results, replay methodology, emulation, or benchmark performance.
