# Tables Plan

| table | chapter | purpose | source |
| --- | --- | --- | --- |
| DASH terminology | 2 | Normalize MPD, Period, Adaptation Set, Representation, Segment | `dash_standard_reference.md` |
| Source inventory | 2 | Show selected literature and role | source inventories |
| ABR families | 2 | Classify baseline families | `state_of_the_art_map.md` |
| Baseline selection | 4 | Justify inclusion/exclusion decisions | `baseline_selection_matrix.md` |
| Signal availability | 4 | Map algorithms to client telemetry | `baseline_signal_matrix.md` |
| Implementation order | 5 | Explain staged build plan | `baseline_implementation_plan.md` |
| Controller readiness gate | 5 | Show the required documents and reviews before implementation | `controller_implementation_readiness_gate.md` |
| Controller traceability | 5 | Link each baseline to source docs, future code modules, tests and smoke scenarios | `controller_traceability_matrix.md` |
| Unit test protocol | 5 | Explain how future tests validate formulas and contract behavior | `controller_unit_test_protocol.md` |
| Fake smoke scenarios | 5/6 | Explain integration checks with fake engine and canonical artifacts | `fake_smoke_validation_protocol.md` |
| Metric validity | 6 | Separate sanity metrics, smoke metrics, future benchmark metrics and forbidden claims | `metric_validity_for_baselines.md` |
| Acceptance criteria | 6 | Define pass/fail evidence | `baseline_acceptance_matrix.md` |
| Phase 2.3 implementation summary | 5 | Summarize implemented controller set, modules, tests, names and units | `baseline_implementation_summary.md` |
| Baseline registry audit | 5 | Show canonical and legacy/debug names preserved in the registry | `baseline_registry_audit.md` |
| Baseline testing summary | 5/6 | Summarize unit coverage by controller and separate tests from performance claims | `baseline_testing_summary.md` |
| Baseline smoke summary | 5/6 | Summarize fake smoke artifact expectations and benchmark boundary | `baseline_smoke_summary.md` |
| Baseline limitations | 6 | Declare simplifications and deferred evaluation methodology | `baseline_limitations.md` |
| Optional candidates | 7 | Show future-work candidates | `optional_candidates.md` |
| Final Phase 2 controller inventory | 5/6 | Show final implemented, optional, historical and deferred controller status | `phase2_controller_inventory.md` |
| Phase 2 academic validity | 5/6 | Define what Phase 2 implementation validity proves and does not prove | `phase2_academic_validity_statement.md` |
| Phase 2 limitations and deferred work | 6/7 | Summarize missing QoE/reward, replay, emulation and benchmark claims | `phase2_open_limitations_and_deferred_work.md` |
| Phase 3 transition | 6/7 | Introduce traces/replay/emulation as the next methodology phase | `phase2_transition_to_phase3.md` |
| Phase 3 trace/replay source inventory | 6 | Classify mandatory, recommended, optional and deferred trace/replay sources | `02_traces_replay/source_inventory.md` |
| Dataset candidate matrix | 6 | Compare trace candidates by source, format, split role, risks and provisional decision | `02_traces_replay/trace_dataset_matrix.md` |
| Dataset selection criteria | 6 | Explain why datasets are not final until provenance, terms and conversion are documented | `02_traces_replay/trace_dataset_selection.md` |
| Replay/emulation comparison | 6 | Compare Mahimahi, `tc/netem` and custom fake trace-driven runner criteria | `02_traces_replay/mahimahi_or_alternatives.md` |
| Split and OOD policy | 6 | Define train, validation, test and OOD roles for later phases | `02_traces_replay/train_validation_test_ood_policy.md` |
| Leakage prevention checklist | 6 | Show controls against trace, parameter, scenario and artifact leakage | `02_traces_replay/leakage_prevention_policy.md` |
| Synthetic trace plan | 6 | Describe future runner validation traces before real datasets | `02_traces_replay/synthetic_trace_test_plan.md` |
| Future run artifact contract | 6 | Define expected manifests, telemetry, summaries and repository exclusions | `02_traces_replay/run_artifact_expectations.md` |
| Phase 3.2A source triage decisions | 6 | Show accepted mandatory/recommended cards, promoted sources and deferred sources | `02_traces_replay/source_triage_decision.md` |
| Phase 3.2A leakage risks by dataset | 6 | Explain sliding-window, route, service/day, operator/device/app, trajectory and causal leakage risks | `02_traces_replay/leakage_prevention_policy.md` |
| Phase 3.2A preliminary split policy | 6 | State first-integration, modern-mobile/OOD, reference-only and metadata-only roles without closing final splits | `02_traces_replay/train_validation_test_ood_policy.md` |

## Conversion Rule

Markdown tables are drafts. Later LaTeX tables should be shorter and split when necessary.
