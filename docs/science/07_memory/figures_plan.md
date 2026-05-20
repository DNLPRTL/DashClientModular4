# Figures Plan

| figure | chapter | purpose | source | status |
| --- | --- | --- | --- | --- |
| DASH client flow | 2 | Explain MPD parsing, segment request, buffer, controller loop | DASH reference plus local architecture | planned |
| Client module architecture | 3 | Show parser/downloader/buffer/engine/controller/logging/evaluation separation | Phase 1 architecture docs | planned |
| Documentation-to-code gate | 4 | Show paper card to implementation spec to tests to code | Phase 2 methodology | planned |
| Baseline family map | 2 | Place rate-based, buffer-based, BOLA, MPC, RobustMPC, optional methods | Field map | planned |
| Signal dependency map | 4 | Show which controller needs which signal | Signal matrix | planned |
| Evaluation path | 6 | Separate fake-engine benchmark path from GStreamer demo path | Phase 1/Phase 2 scope | planned |
| Validation ladder | 5/6 | Separate unit tests, fake smoke, readiness, future replay and final QoE claims | controller validation protocols | planned |
| Python development timeline | 4/5 | Show incremental hardening before controller implementation | `python_development_narrative_plan.md` | planned |
| Controller traceability flow | 5 | Show source evidence -> spec -> mapping -> tests -> code -> memory | `controller_traceability_matrix.md` | planned |
| Phase 2.3 closure boundary | 5/6 | Show what implementation closure proves and what waits for replay/QoE | `baseline_phase2_3_closure_report.md`, `chapter_06_pre_evaluation_boundary.md` | planned |

## Figure Policy

All figures should be original diagrams unless explicit permission exists. Do not copy paper figures into the repository or thesis.
