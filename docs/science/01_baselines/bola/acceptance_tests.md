# bola Acceptance Tests

These tests specify and track the Phase 2.3.4 BOLA-basic behavior implemented in `core/controller/bola.py` and covered by `tests/test_bola_controller.py`.

## Unit Tests

Assume rates `[100, 200, 400]` bytes/s, `segment_duration_s = 4.0`, `V = 5.0`, `gamma = 0.2`, `utility = ln(rate/min_rate)`, and normalized size units unless stated otherwise.

| test | input | expected result | tolerance |
| --- | --- | --- | --- |
| invalid buffer | buffer missing, negative, or non-finite | target `100`, level `0` | exact |
| invalid duration | duration `0` or negative | target `100`, level `0` | exact |
| low buffer fallback | buffer `3.0`, duration `4.0` | target `100`, level `0` | exact |
| low valid score region | buffer `2.0` if fallback disabled for fixture | argmax score level `0` | exact argmax |
| medium buffer | buffer `12.0` | argmax score level `1`, target `200` | exact argmax |
| higher buffer | buffer `24.0` | argmax score level `2`, target `400` | exact argmax |
| all negative score policy | buffer so high all scores are non-positive | target `100`, level `0` | exact |
| one-level ladder | rates `[300]` | target `300`, level `0` | exact |
| no throughput input | missing size/time throughput data | decision still succeeds from buffer/ladder/duration | exact |
| invalid parameter | `V <= 0` or non-finite `gamma` | documented default fallback | exact |

Implemented additional checks:

- `bola` is registered while `min_rate`, `fixed_rate`, `max_rate`, `rate_based`, `bba`, `fixed_quality`, `scripted_quality`, and `max_quality` remain available.
- Returned `target_rate` is a `float` in bytes/s and `quality_level` is the representation index produced by `quantizeRate`.
- `rates_unit` conversions from bits/s to bytes/s are explicit.
- Throughput fields, future bandwidth/oracle fields, TCP RTT/loss/cwnd, server state, console/log/progress fields, and RL/Pensieve fields do not influence the BOLA-basic decision.
- Missing exact sizes use `rate * fragment_duration`; optional exact positive per-level sizes are accepted.
- Empty/malformed ladders return the safe `0.0` fallback without crashing.
- All non-positive BOLA scores select the minimum rate because the current controller contract does not express no-download/wait.

## Fake Smoke Tests

| scenario | setup | expected result | what it proves |
| --- | --- | --- | --- |
| standard stable fake run | fake engine with `controller.name: bola` | canonical artifacts exist and manifest records `bola` | integration only |
| low buffer / richer buffer zones | deferred until replay/traces or a controlled fake scenario fixture can express reproducible buffer regimes without runtime changes | documented deferral | scope boundary |
| missing segment size matrix | standard fake path provides rates and segment duration only | controller uses `rate * duration` approximation | approximation path |
| dash.js features absent | run without DYNAMIC/FAST SWITCHING state | controller still works | BOLA-basic boundary |

Smoke outputs are not benchmark results.

## Minimum Scenarios

- Empty ladder safe `0.0` fallback.
- Single representation.
- Invalid buffer.
- Invalid duration.
- Valid score computation over at least three ladder levels.
- Missing exact segment sizes.
- Optional exact segment sizes when supplied by tests.
- Forbidden signal invariants.

## Invariants

- No explicit bandwidth prediction is required.
- Target rate unit is bytes per second.
- Output quantizes to a valid representation index.
- BOLA utility is controller-internal and not final QoE.
- The controller is labeled BOLA-basic.

## Invalidating Failures

- Implementing DYNAMIC under the name `bola`.
- Implementing FAST SWITCHING behavior.
- Claiming production dash.js equivalence.
- Using throughput as the main BOLA decision signal.
- Treating fake smoke output as benchmark evidence.
- Modifying runtime/player/metric/config files.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These tests validate deterministic BOLA-basic controller behavior only. Fake smoke validates integration and canonical artifact production only. They do not validate final QoE, production BOLA-E, DYNAMIC, FAST SWITCHING, replay, or benchmark performance.
