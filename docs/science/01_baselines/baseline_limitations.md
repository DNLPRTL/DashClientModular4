# Baseline Limitations

Phase 2.3 closes implementation readiness for mandatory baseline controllers, not final evaluation.

## Methodological Limits

- Fake smoke is not a final benchmark.
- No final QoE/reward exists yet.
- No trace, replay or network emulation methodology exists yet.
- No real-network comparative evaluation exists yet.
- GStreamer is integration/demo evidence, not benchmark-grade evidence.
- Canonical CSVs are reproducibility and future-evaluation artifacts, not final training datasets or final scores.

## Controller Simplifications

| controller | documented simplification |
| --- | --- |
| `rate_based` | application-layer throughput only, safety factor, EWMA/conservative logic and low-buffer guard |
| `bba` | BBA-0 reservoir/cushion map with no advanced startup estimator or Netflix production internals |
| `bola` | BOLA-basic only, with exact or approximated segment sizes; no DYNAMIC, FAST SWITCHING, BOLA-E or full dash.js production behavior |
| `mpc` | small-horizon enumerative MPC with bounded sequence count; no FastMPC table compression |
| `robust_mpc` | conservative MPC prediction correction; no Pensieve, RL, neural inference, training or ABR server path |

## Claim Boundary

The project can now claim that the mandatory baseline controllers are implemented, registered, unit-tested and contract-compatible. It cannot yet claim:

- `bola` beats `bba`;
- MPC or RobustMPC improves QoE;
- RobustMPC reproduces Pensieve performance;
- fake smoke results are benchmark results;
- GStreamer timing proves real playback QoE;
- generated CSVs are valid final training data.

Comparisons and paper-level claims require Phase 3, Phase 3.5 and Phase 6 methodology.

## Phase 2.4 Formal Closure Pointer

The final Phase 2 limitations and deferred-work statement is `phase2_open_limitations_and_deferred_work.md`.
