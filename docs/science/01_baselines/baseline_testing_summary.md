# Baseline Testing Summary

Phase 2.3 unit tests validate controller decision logic, registry visibility, unit handling and forbidden-signal boundaries. They intentionally use small deterministic fixtures instead of videos, external traces, network emulation or final QoE formulas.

| controller | test module | coverage summary |
| --- | --- | --- |
| `min_rate`, `fixed_rate`, `max_rate` | `tests/test_sanity_rate_controllers.py` | min/fixed/max selection, level/rate clamping, invalid ladders, one-level ladders, target-rate unit conversion and no-console behavior |
| `rate_based` | `tests/test_rate_based_controller.py` | safe throughput estimation, bytes/time derivation, safety factor, EWMA/conservative upshift, aggressive downshift, low-buffer guard, unit conversions, invalid ladders and forbidden network/server/oracle fields |
| `bba` | `tests/test_bba_controller.py` | reservoir and cushion thresholds, monotonic buffer mapping, invalid buffer handling, invalid parameter defaults, ladder bounds, throughput independence and forbidden network/text/oracle fields |
| `bola` | `tests/test_bola_controller.py` | BOLA-basic utility/buffer score, low/high buffer behavior, no throughput prediction requirement, exact and approximated segment-size paths, all-non-positive-score fallback, invalid inputs and forbidden DYNAMIC/FAST SWITCHING/RL-style fields |
| `mpc` | `tests/test_mpc_controller.py` | horizon enumeration, harmonic mean predictor, measured throughput history, buffer/rebuffer simulation, internal objective terms, first-action return, segment-size modeling, horizon cap, invalid inputs and forbidden future/QoE/RL fields |
| `robust_mpc` | `tests/test_robust_mpc_controller.py` | MPC compatibility, zero-error equivalence, prediction-error correction, conservative behavior under high error, startup fallback, bounded error window, persistent prediction alignment, invalid inputs and no Pensieve/RL dependency |
| all registered baselines | `tests/test_baseline_registry_audit.py` | canonical and legacy registry availability, registry key/spec consistency, callable controller API surface and absence of final QoE/reward constructor requirements |

## What Unit Tests Prove

- A controller returns a contract-compatible target rate for deterministic fixtures.
- Target rates are interpreted as bytes per second.
- Quantized quality levels are representation indices.
- Controller decisions stay inside the active ladder or fail safely on invalid ladders.
- Each academic baseline uses the intended primary signal family.
- Forbidden fields such as TCP RTT, packet loss, server state, future oracles, console text, Pensieve/RL state and final QoE/reward fields do not drive Phase 2.3 decisions.

## What Unit Tests Do Not Prove

- They do not prove final performance.
- They do not compare algorithms academically.
- They do not define or validate final QoE/reward.
- They do not replace replay, traces, emulation or benchmark methodology.
- They do not make GStreamer playback benchmark-grade.

Final comparative results wait for later replay/traces/QoE phases.
