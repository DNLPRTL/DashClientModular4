# Optional Candidates

Optional candidates are documented to prevent scope drift. They must not enter the initial implementation order unless a later decision promotes them and creates the full five-document package.

| candidate | family | current role | promotion condition | current decision |
| --- | --- | --- | --- | --- |
| FESTIVE | fairness/efficiency/stability oriented | optional historical candidate | only if multi-client fairness becomes a TFG question | do not implement initially |
| PANDA | probe-and-adapt throughput control | optional throughput-family candidate | only if rate_based needs a stronger throughput comparator | do not implement initially |
| Oboe | ABR auto-tuning | optional adaptive parameter candidate | only if parameter tuning becomes a research question | do not implement initially |
| SODA | modern smoothness optimized non-neural controller | strongest modern optional non-neural candidate | only after mandatory baselines and QoE methodology are stable | document only |
| RBC | backup optional | fallback placeholder | only after bibliographic identity and value are locked | backup only |
| Lumos | learning/estimation-oriented modern candidate | optional modern candidate | only after source intake and scope review | do not implement initially |
| WISH | commercial/product ABR candidate | optional practical candidate | only if public technical details are sufficient for reproducible implementation | do not implement initially |

## Rule

Candidate cards are not implementation specs. A candidate must be promoted through an explicit scope decision before code starts.

## Phase 2 Closure Status

Phase 2 closes with SODA documented as the strongest modern optional non-neural candidate and RBC kept as backup optional. Neither is implemented or benchmarked.
