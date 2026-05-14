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
| Optional candidates | 7 | Show future-work candidates | `optional_candidates.md` |

## Conversion Rule

Markdown tables are drafts. Later LaTeX tables should be shorter and split when necessary.
