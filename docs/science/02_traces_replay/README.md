# Phase 3 Trace Replay Methodology

This folder is the Phase 3.1 documentation scaffold for trace, dataset, replay and emulation methodology.

Phase 1 closed the client hardening work. Phase 2 closed the baseline controller implementation set: `min_rate`, `fixed_rate`, `max_rate`, `rate_based`, `bba`, `bola`, `mpc` and `robust_mpc`. Phase 3 does not add a new controller. It defines how future evaluations can expose those existing controllers to reproducible network conditions without changing the player, media engines, metric definitions or controller APIs.

## Objective

Define the evidence base and decision gates for selecting throughput traces, replay tools, emulation tools and synthetic test scenarios before any benchmark ranking or final QoE/reward is attempted.

## Questions Phase 3 Must Close

1. Which trace datasets are scientifically relevant, available, legally usable and small enough to integrate without repository bloat?
2. Which datasets should be candidates for train, validation, test and out-of-distribution evaluation?
3. Which sources are only methodological references and which sources are actual trace candidates?
4. Is the project better served by Mahimahi, Linux `tc/netem`, a custom fake trace-driven runner, or a combination?
5. What conversion rules are required before a dataset can become a replay input?
6. How will trace leakage be prevented if later phases introduce tuning, learning or parameter selection?
7. Which synthetic traces are needed to test a future runner before real datasets are used?
8. Which run artifacts should exist in future experiments, and which artifacts must stay out of git?

## Relationship With Phase 2 Controllers

Phase 3 treats the Phase 2 controllers as frozen evaluation subjects. The trace/replay methodology may exercise their existing inputs, but it must not modify controller logic, controller names, player behavior, media engines or metric definitions.

The methodology must preserve the existing separation between parser, segment download, buffer, playback engine, ABR control, logging and evaluation. If a future runner is implemented, it must feed controlled network behavior through an approved boundary rather than embedding trace assumptions into controllers.

## Explicit Non-Goals

- no dataset download;
- no replay implementation;
- no final QoE/reward definition;
- no benchmark ranking;
- no IA/RL implementation;
- no controller changes;
- no player changes;
- no media engine changes;
- no GStreamer benchmark;
- no generated artifacts;
- no PDFs in the repository;
- no logs, CSVs, ZIPs or media in the repository;
- no `pytest`.

## Directory Map

| document | purpose |
| --- | --- |
| `source_inventory.md` | Initial source categories and decisions for trace/replay literature and datasets. |
| `search_protocol.md` | Repeatable literature and dataset search methodology. |
| `trace_dataset_selection.md` | Dataset selection criteria and decision workflow. |
| `trace_dataset_matrix.md` | Candidate dataset matrix with risk and split columns. |
| `trace_dataset_card_template.md` | Template for future per-dataset cards. |
| `method_card_template.md` | Template for future replay/emulation method cards. |
| `replay_emulation_decision.md` | Decision criteria for replay, emulation and fake trace-driven execution. |
| `mahimahi_or_alternatives.md` | Comparison of Mahimahi, `tc/netem` and a custom fake runner. |
| `generalization_protocol.md` | Generalization and OOD evaluation planning rules. |
| `evaluation_network_scenarios.md` | Scenario taxonomy for later evaluation design. |
| `train_validation_test_ood_policy.md` | Split policy for future tuning, learning and reporting. |
| `leakage_prevention_policy.md` | Controls against trace, parameter and artifact leakage. |
| `replay_runner_requirements.md` | Requirements for a future runner without implementing it. |
| `synthetic_trace_test_plan.md` | Synthetic trace plan for future runner validation. |
| `run_artifact_expectations.md` | Expected future run artifacts and repository hygiene. |
| `phase3_memory_notes.md` | Thesis memory and defense usage notes. |
| `trace_dataset_cards/` | Placeholder for later dataset cards. |
| `method_cards/` | Placeholder for later method cards. |

## Current Decision Boundary

No dataset is final until `trace_dataset_selection.md` is completed. No dataset is downloaded into the repository. Full Puffer raw data remains metadata-only in Phase 3.1. FCC raw data remains reference-only until a conversion and storage plan exists. Mahimahi is a method candidate, not a mandatory implementation. `tc/netem` is a fallback or complementary method candidate. A custom fake trace-driven runner is the primary likely implementation candidate for reproducible Python tests, but this phase only documents requirements.

