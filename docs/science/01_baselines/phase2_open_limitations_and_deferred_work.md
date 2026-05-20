# Phase 2 Open Limitations And Deferred Work

Phase 2 closes baseline implementation readiness. It deliberately leaves evaluation methodology and advanced controller families for later phases.

## Evaluation Limitations

- No final QoE/reward is defined.
- No trace replay system is built.
- No network emulation methodology is selected.
- No Mahimahi or alternative emulation decision is made.
- No final benchmark is run.
- No real-network ranking is claimed.
- No train/test/OOD split is defined.
- No IA/RL comparison is possible yet.

## Runtime And Engine Limits

- GStreamer remains integration/demo only.
- The fake engine is controlled validation only.
- Fake smoke validates integration and artifacts, not performance.
- Canonical runtime CSVs are reproducibility artifacts, not final benchmark datasets.
- Runtime/player/media-engine behavior is not changed by Phase 2.4 closure documentation.

## Controller Limits

| controller or method | declared limitation |
| --- | --- |
| `min_rate`, `fixed_rate`, `max_rate` | technical controls only, not academic ABR baselines |
| `rate_based` | application-layer throughput baseline with documented safety and smoothing parameters, not TCP-level modeling |
| `bba` | BBA-0 style behavior, not Netflix production internals |
| `bola` | BOLA-basic only, not production dash.js, BOLA-E, DYNAMIC or FAST SWITCHING |
| `mpc` | small-horizon enumerative MPC, not FastMPC |
| `robust_mpc` | classical robust MPC correction, not Pensieve, RL or neural inference |
| SODA | optional modern candidate, not implemented |
| RBC | optional backup candidate, not implemented |
| Pensieve | historical IA/RL reference only, not implemented |
| DYNAMIC | deferred practical dash.js-derived method |
| FAST SWITCHING | deferred practical dash.js-derived method |

## Deferred Work

Phase 3 should address traces, replay and emulation. Later evaluation phases should define final QoE/reward, benchmark interpretation, scenario design, result reporting and statistical/experimental validity. AI/RL work must remain deferred until reward, training data, simulator/replay and leakage rules are explicitly defined.

## Claim Boundary

The correct Phase 2 claim is:

The mandatory baseline controllers are documented, implemented, registered, unit-tested and integration-ready.

The incorrect Phase 2 claims are:

- one controller is better than another;
- fake smoke is a benchmark;
- GStreamer demo timing is final QoE;
- internal controller objectives are final reward;
- RobustMPC reproduces Pensieve;
- production dash.js behavior has been implemented.
