# Phase 2 Tables And Figures Final Plan

This document lists the final tables and figures that should be created later for the TFG memory from Phase 2 evidence. They should be original thesis material, not copied paper figures.

## Final Tables

| table | purpose | source document |
| --- | --- | --- |
| Baseline selection table | justify mandatory, optional and deferred methods | `baseline_selection_matrix.md` |
| Controller inventory table | summarize category, module, registry name, tests, source docs and benchmark status | `phase2_controller_inventory.md` |
| Signal mapping table | map controllers to available client signals and units | `baseline_signal_matrix.md` |
| Implementation/test traceability table | link source evidence, spec, code and tests | `controller_traceability_matrix.md`, `phase2_test_validation_summary.md` |
| Limitation table | declare no QoE/reward, no replay, no benchmark and controller simplifications | `phase2_open_limitations_and_deferred_work.md` |
| Registry table | show canonical names and legacy/debug names | `baseline_registry_audit.md` |
| Evidence ladder table | separate unit tests, smoke, readiness, future replay and final benchmark evidence | `phase2_academic_validity_statement.md` |

## Final Figures

| figure | purpose | source document |
| --- | --- | --- |
| Controller pipeline diagram | show config -> registry -> feedback -> controller -> quantization -> segment request | `baseline_entry_contract.md` |
| Paper to implementation diagram | show paper -> source_evidence -> spec -> mapping -> tests -> code -> smoke | `phase2_academic_validity_statement.md` |
| Phase 2 to Phase 3 transition diagram | show baseline closure feeding trace/replay/emulation methodology | `phase2_transition_to_phase3.md` |
| Validation ladder diagram | distinguish unit, smoke, readiness, replay/emulation and benchmark claims | `phase2_test_validation_summary.md` |
| Baseline family map | place selected and deferred baselines by ABR family | `baseline_selection_matrix.md` |
| MPC planning sketch | explain receding-horizon first-action behavior | `mpc/implementation_spec.md` |
| RobustMPC correction sketch | explain conservative prediction adjustment | `robust_mpc/implementation_spec.md` |

## Figure And Table Policy

- Keep diagrams original.
- Cite source documents and papers, but do not copy paper figures.
- Keep benchmark-looking tables empty until final evaluation methodology exists.
- Do not include generated CSVs, logs or run artifacts in the thesis repository as source material.
