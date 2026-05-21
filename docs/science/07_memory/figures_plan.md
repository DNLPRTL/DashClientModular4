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
| Paper to implementation evidence chain | 5 | Show paper/source evidence -> spec -> mapping -> tests -> code -> smoke | `phase2_academic_validity_statement.md` | planned |
| Phase 2 to Phase 3 transition | 6/7 | Show baseline closure feeding trace/replay/emulation methodology | `phase2_transition_to_phase3.md` | planned |
| Trace methodology pipeline | 6 | Show search -> inventory -> cards -> selection -> conversion -> future evaluation gates | `02_traces_replay/search_protocol.md`, `trace_dataset_selection.md` | planned |
| Replay/emulation decision flow | 6 | Show Mahimahi, `tc/netem`, custom fake runner and hybrid decision criteria | `02_traces_replay/replay_emulation_decision.md` | planned |
| Dataset split and OOD boundary | 6 | Show train, validation, test and OOD separation | `02_traces_replay/train_validation_test_ood_policy.md` | planned |
| Leakage prevention map | 6 | Show how trace, parameter, scenario and artifact leakage are avoided | `02_traces_replay/leakage_prevention_policy.md` | planned |
| Run artifact lifecycle | 6 | Show raw data outside repo, generated artifacts outside repo and authored summaries in docs | `02_traces_replay/run_artifact_expectations.md` | planned |
| Dataset domain ladder | 6 | Show synthetic, HSDPA, LTE, HAS, 4G KPI, 5G KPI, mmWave 5G, FCC and Puffer roles | `02_traces_replay/generalization_protocol.md`, `02_traces_replay/source_triage_decision.md` | planned |
| Phase 3.2A evaluation pipeline | 6 | Show source pages/distilled notes -> cards -> matrix -> schema -> runner -> later metrics -> later comparison | `02_traces_replay/source_triage_decision.md`, `02_traces_replay/replay_runner_requirements.md` | planned |
| Trace schema boundary | 6 | Show raw source -> converter -> normalized schema v1 -> manifest -> future runner | `02_traces_replay/common_trace_schema.md`, `02_traces_replay/trace_manifest_schema.md` | planned |
| External trace storage layout | 6 | Show repository docs separated from raw, normalized and manifest directories outside git | `02_traces_replay/trace_directory_layout.md` | planned |

## Figure Policy

All figures should be original diagrams unless explicit permission exists. Do not copy paper figures into the repository or thesis.
