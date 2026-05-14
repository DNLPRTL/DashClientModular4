# Scope Decision

## Included Later

| item | decision | reason |
| --- | --- | --- |
| Sanity controllers | include first | They validate controller plumbing, configuration, and deterministic telemetry without claiming ABR novelty. |
| Rate-based | include | It is the simplest academic throughput-driven baseline and uses signals expected from segment downloads. |
| BBA | include | It isolates buffer occupancy as the primary signal and gives a clean contrast to throughput-based control. |
| BOLA | include | It is a major buffer/utility baseline and has practical dash.js relevance. |
| MPC | include | It represents QoE optimization with throughput prediction and buffer state. |
| RobustMPC | include | It is a standard robust variant used for comparison in Pensieve-style evaluations. |

## Excluded Initially

| item | decision | reason |
| --- | --- | --- |
| SODA | optional only | Strong modern non-neural candidate, but not needed for the first baseline set and likely higher implementation cost. |
| Pensieve | do not implement | Historical neural/RL reference only; training, model handling, and reward design are out of scope for this block. |
| dash.js DYNAMIC | defer | Hybrid production behavior would blur the clean initial comparison among academic baselines. |
| dash.js FAST SWITCHING | defer | Runtime switching semantics are not part of the initial baseline comparison. |
| RBC | backup optional | Keep as fallback only if a future comparison gap appears. |
| Replay/traces | defer | Needed later for benchmarking, but not part of this documentation block. |
| Final QoE/reward | defer | MPC-family implementation will require this later; this block only marks dependency. |
| AI/RL controller | defer | Requires a separate scientific and engineering track. |

## Boundary

Only `docs/science/**` is in scope for this block. Runtime code, player code, metrics, configs, traces, datasets, generated artifacts, and PDFs are out of scope.
