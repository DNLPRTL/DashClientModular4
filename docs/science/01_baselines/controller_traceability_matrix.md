# Controller Traceability Matrix

| controller | source paper | source_evidence | implementation_spec | mapping | acceptance_tests | expected code module | expected test module | smoke scenario | memory chapter | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sanity_controllers | local sanity specs | N/A | `sanity_controllers/*.md` | `baseline_entry_contract.md` | `sanity_controllers/acceptance_tests.md` | `core/controller/sanity_rate.py` | `tests/test_sanity_rate_controllers.py` | single ladder, min/fixed/max deterministic fake run | Chapter 5 validation path | implemented as technical controls, not academic baselines |
| rate_based | `rate_based/paper_card.md` | `rate_based/source_evidence.md` | `rate_based/implementation_spec.md` | `rate_based/controller_api_mapping.md` | `rate_based/acceptance_tests.md` | `core/controller/rate_based.py` | `tests/test_rate_based_controller.py` | stable fake integration smoke now; low/drop scenarios deferred until replay/traces or controlled capacity fixture | Chapters 2, 5, 6 later | implemented in Phase 2.3.2 as the first academic ABR baseline; no benchmark claim |
| bba | `bba/paper_card.md` | `bba/source_evidence.md` | `bba/implementation_spec.md` | `bba/controller_api_mapping.md` | `bba/acceptance_tests.md` | `core/controller/bba.py` | `tests/test_bba_controller.py` | standard fake integration smoke now; richer low/cushion scenarios deferred until replay/traces or controlled fake scenario fixture | Chapters 2, 5, 6 later | implemented in Phase 2.3.3 as the second academic ABR baseline; no benchmark claim |
| bola | `bola/paper_card.md`, `bola/dashjs_source_card.md` | `bola/source_evidence.md`, `bola/dashjs_practical_evidence.md` | `bola/implementation_spec.md` | `bola/controller_api_mapping.md` | `bola/acceptance_tests.md` | `core/controller/bola.py` | `tests/test_bola_controller.py` | standard fake integration smoke now; richer low/high buffer scenarios deferred until replay/traces or controlled fake scenario fixture | Chapters 2, 5, 6 later | implemented in Phase 2.3.4 as the third academic ABR baseline; BOLA-basic only, no benchmark claim |
| mpc | `mpc/paper_card.md` | `mpc/source_evidence.md` | `mpc/implementation_spec.md` | `mpc/controller_api_mapping.md` | `mpc/acceptance_tests.md` | `core/controller/mpc.py` | `tests/test_mpc_controller.py` | standard fake integration smoke now; richer low-capacity scenario deferred until replay/traces or controlled fake capacity fixture | Chapters 2, 5, 6 later | implemented in Phase 2.3.5 as the fourth academic ABR baseline; internal objective only, no benchmark claim |
| robust_mpc | `robust_mpc/paper_card.md`, `robust_mpc/pensieve_source_artifact_card.md` | `robust_mpc/source_evidence.md` | `robust_mpc/implementation_spec.md` | `robust_mpc/controller_api_mapping.md` | `robust_mpc/acceptance_tests.md` | `core/controller/robust_mpc.py` | `tests/test_robust_mpc_controller.py` | standard fake integration smoke now; richer low/unstable capacity scenario deferred until replay/traces or controlled fake capacity fixture | Chapters 2, 5, 6 later | implemented in Phase 2.3.6 as the fifth academic ABR baseline; Pensieve/RL excluded, no benchmark claim |

## Traceability Rule

Any future code module must cite its local Markdown spec in comments or developer notes. If implementation behavior diverges from this matrix, update the science docs before merging code.

## Phase 2.3 Closure Audit

The implementation set above is closed by:

- `baseline_implementation_summary.md`
- `baseline_registry_audit.md`
- `baseline_testing_summary.md`
- `baseline_smoke_summary.md`
- `baseline_limitations.md`
- `baseline_phase2_3_closure_report.md`

These documents aggregate existing paper/spec/code/test evidence and do not introduce new controllers, replay, QoE/reward, benchmark claims, generated artifacts or media assets.
