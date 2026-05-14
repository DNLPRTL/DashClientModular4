# Controller Code Review Checklist

Use this checklist during future Phase 2.3 controller implementation reviews.

## Scope Boundary

| check | pass condition |
| --- | --- |
| No player rewrite | `player.py` is untouched unless a separate approved scope requires it. |
| No metric definition change | Existing metrics and benchmark gates are not redefined. |
| No hidden benchmark claim | Docs, code comments and logs do not claim final performance. |
| No console dependency | Controller reads feedback, not console/progress/log text. |
| No hardcoded local paths | No user-machine paths, local MPDs, PDFs or data folders in code. |
| No PDF/code import from papers | Implementation comes from Markdown specs and source evidence. |
| No external dataset download | Unit and smoke tests use small fixtures or fake engine. |
| Determinism | Any randomness is absent or explicitly seeded and justified. |
| Python 3.8 compatible | Syntax and typing support Python 3.8. |
| `unittest`, not `pytest` | New code tests follow repository test framework. |

## Implementation Match

| check | pass condition |
| --- | --- |
| Spec alignment | Code follows `implementation_spec.md`. |
| API mapping alignment | Every signal used appears in `controller_api_mapping.md`. |
| Acceptance coverage | Tests cover `acceptance_tests.md`. |
| Units documented | Comments or constants clarify bytes/s, seconds, indices and ratios. |
| Formula comments | Non-obvious formulas cite the local spec, not raw PDF pages. |
| Safe fallback | Missing or invalid input follows documented fallback. |
| Ladder safety | No level outside the ladder can be returned. |
| Config clarity | Parameters have defaults and validation where needed. |

## Controller-Specific Review Points

| controller | review focus |
| --- | --- |
| rate_based | Application-layer throughput only; safety factor; up/down rules. |
| bba | Buffer primary; reservoir/cushion thresholds; no throughput primary rule. |
| bola | BOLA-basic only; no DYNAMIC/FAST SWITCHING/BOLA-E; utility is internal. |
| mpc | Bounded enumeration; internal objective not final QoE; no future oracle. |
| robust_mpc | Prediction-error alignment; no Pensieve/RL/model/training path. |

## Artifact And Runtime Hygiene

- Controller must not write `segment_telemetry.csv` or `evaluation_segments.csv` directly.
- Controller must not produce `dataset.csv` or `dataset_training.csv`.
- Controller must not mutate `eval_phase` or `use_for_eval`.
- Controller must not parse `run.log`.
- GStreamer behavior must remain integration/demo only.

## Review Outcome Labels

| label | meaning |
| --- | --- |
| approve | Matches spec, tests and boundaries. |
| approve with docs follow-up | Code is correct but docs need a clarifying note before merge. |
| block | Uses forbidden signals, changes runtime scope, lacks tests, or creates claims. |
