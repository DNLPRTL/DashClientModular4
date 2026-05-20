# Science Documentation

This directory is the scientific documentation scaffold and closure record for DashClientModular4.

Phase 1 closed with the client certified as ABR-neutral, reproducible, and testable. Phase 2 selected, documented, implemented and validated the mandatory ABR baseline set. Phase 3 now documents trace, dataset, replay and emulation methodology before any final benchmark or QoE/reward is attempted.

## Methodology Gate

No academic ABR baseline may be implemented directly from a raw paper or PDF.

Before implementation, each implemented baseline must have these Markdown artifacts:

1. `paper_card.md`
2. `implementation_spec.md`
3. `controller_api_mapping.md`
4. `acceptance_tests.md`
5. `notes_for_memory.md`

The paper card captures the scientific source. The implementation specification turns the paper into deterministic engineering requirements. The controller API mapping confirms the client signals and abstractions needed. The acceptance tests define minimum behavioral evidence. The memory notes connect the work to the final TFG thesis.

## Directory Map

| path | purpose |
| --- | --- |
| `00_field_map/` | DASH background, survey map, local related work, scope decisions, and source cards. |
| `01_baselines/` | Baseline selection matrices, signal analysis, implementation order, templates, and baseline cards. |
| `02_traces_replay/` | Phase 3 trace/dataset/replay/emulation methodology scaffold and decision gates. |
| `07_memory/` | Thesis-memory integration notes for the UGR/ETSIIT LaTeX template, citations, figures, tables, annexes, and defense constraints. |

## Current Decisions

- Phase 2 baseline closure: `01_baselines/phase2_baseline_closure.md`.
- Implemented sanity controllers: `min_rate`, `fixed_rate`, `max_rate`.
- Implemented academic baselines: `rate_based`, `bba`, `bola`, `mpc`, `robust_mpc`.
- Do not implement initially: SODA, Pensieve, dash.js DYNAMIC, dash.js FAST SWITCHING.
- Keep RBC only as a backup optional candidate.
- Defer the final QoE/reward definition.
- Defer trace replay, datasets, emulation, and benchmark implementation.
- Defer any AI/RL controller.
- Keep GStreamer as integration/demo, not benchmark-grade.
- Use the fake engine as the controlled path for future tests, replay, and benchmarking.
- Phase 3.1 records trace/replay source candidates, dataset selection criteria, replay/emulation criteria, split policy, leakage prevention, synthetic trace test planning and artifact expectations.
- No Phase 3.1 dataset is final and no dataset is downloaded into the repository.
- Full Puffer raw data is metadata-only in Phase 3.1.
- FCC Measuring Broadband America raw data is reference-only until a conversion/download plan exists.
- Mahimahi is a method candidate, not mandatory implementation.
- A custom fake trace-driven runner is the primary likely implementation candidate for reproducible Python tests, but is not implemented in Phase 3.1.

## Source Handling Rules

- Do not add raw PDFs to the repository.
- Do not copy long passages from papers or standards.
- Do not copy paper figures into the thesis or repository unless explicit permission is available.
- Prefer original diagrams in the thesis.
- Use ISO/IEC 23009-1:2022 only as a bibliographic and terminological reference.
- Keep every implementation decision traceable to Markdown source cards and matrices.
