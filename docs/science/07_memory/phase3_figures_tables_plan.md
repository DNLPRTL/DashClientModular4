# Phase 3 Figures Tables Plan

This plan tracks figures and tables that may support the Phase 3 methodology section of the memory.

## Candidate Figures

| id | title | purpose | source |
| --- | --- | --- | --- |
| P3-F1 | Trace methodology pipeline | Show search, inventory, carding, selection, conversion and evaluation gates. | `02_traces_replay/README.md`, `search_protocol.md` |
| P3-F2 | Replay/emulation decision flow | Compare Mahimahi, `tc/netem` and custom fake runner decisions. | `replay_emulation_decision.md` |
| P3-F3 | Dataset split and OOD boundary | Show train, validation, test and OOD separation. | `train_validation_test_ood_policy.md` |
| P3-F4 | Leakage prevention map | Show how trace, parameter, scenario and artifact leakage are blocked. | `leakage_prevention_policy.md` |
| P3-F5 | Run artifact lifecycle | Show raw traces outside repo, generated outputs outside repo and authored summaries in docs. | `run_artifact_expectations.md` |
| P3-F6 | Dataset domain ladder | Show synthetic, HSDPA, LTE, HAS, 4G KPI, 5G KPI, mmWave 5G, FCC and Puffer roles. | `generalization_protocol.md`, `source_triage_decision.md` |

## Candidate Tables

| id | title | purpose | source |
| --- | --- | --- | --- |
| P3-T1 | Trace/replay source inventory | Classify mandatory, recommended, optional and deferred sources. | `source_inventory.md` |
| P3-T2 | Dataset candidate matrix | Compare availability, format, split role and risks. | `trace_dataset_matrix.md` |
| P3-T3 | Dataset selection criteria | Explain why no dataset is final yet. | `trace_dataset_selection.md` |
| P3-T4 | Replay/emulation method comparison | Compare Mahimahi, `tc/netem` and custom fake runner. | `mahimahi_or_alternatives.md` |
| P3-T5 | Synthetic trace suite | Document future runner validation inputs. | `synthetic_trace_test_plan.md` |
| P3-T6 | Expected run artifacts | Define future artifact contract and git exclusions. | `run_artifact_expectations.md` |
| P3-T7 | Source triage decisions | Show mandatory, recommended, reference-only and metadata-only source decisions. | `source_triage_decision.md` |
| P3-T8 | Leakage risks by dataset | Summarize route, service/day, operator/device/app, trajectory and causal leakage risks. | `leakage_prevention_policy.md` |
| P3-T9 | Candidate split policy | Summarize preliminary roles without closing a final split. | `train_validation_test_ood_policy.md` |

## Policy

All figures must be original diagrams. Do not copy figures from papers or websites. Do not commit generated plots unless a later thesis-figure decision explicitly approves them.

## Phase 3.2A Source-Triage Update

The preferred Chapter 6 visual sequence is:

1. evaluation pipeline: source pages and distilled notes -> cards -> matrix -> trace schema -> runner -> Phase 3.5 metrics -> Phase 6 comparison;
2. replay method decision tree: Python runner first, Mahimahi secondary, netem fallback;
3. dataset domain ladder from synthetic traces to real-world references.
