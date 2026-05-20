# Implementation Chapter Traceability

This document maps future implementation evidence to the TFG memory. It is a planning document, not the final chapter.

## Chapter 5 Structure

| section | content | evidence docs | figures/tables |
| --- | --- | --- | --- |
| Client architecture | Module boundaries: parser, downloader, media engine, controller, logging, artifacts. | Phase 1 architecture docs and readiness report. | Client architecture figure. |
| Controller contract | Feedback keys, units, target rate, quality index, ladder source. | `baseline_entry_contract.md`, API mappings. | Controller contract table. |
| Baseline implementation method | Documentation-first gate before coding. | `controller_implementation_readiness_gate.md`, `controller_academic_validation_protocol.md`. | Implementation gate figure. |
| Sanity controllers | Deterministic `min_rate`, `fixed_rate`, and `max_rate` behavior for registry, unit, contract and fake-engine validation. | `sanity_controllers/*.md`, `core/controller/sanity_rate.py`, `tests/test_sanity_rate_controllers.py`. | Sanity controller table. |
| Academic baselines | `rate_based` implemented first, `bba` implemented second, `bola` implemented third as BOLA-basic, `mpc` implemented fourth as small-horizon enumerative MPC, and `robust_mpc` implemented fifth as MPC with conservative prediction correction. | implementation specs, controller mappings, `tests/test_rate_based_controller.py`, `tests/test_bba_controller.py`, `tests/test_bola_controller.py`, `tests/test_mpc_controller.py`, and `tests/test_robust_mpc_controller.py`. | Baseline traceability matrix. |
| Testing strategy | Unit tests, fake smoke tests, readiness checks. | unit and fake smoke protocols. | Test pyramid or validation ladder figure. |
| Reproducibility | Canonical artifacts and environment/config capture. | output artifact contract and fake smoke protocol. | Artifact flow figure. |
| Limitations | No final QoE, no benchmark claims, no replay/traces, no AI/RL. | metric validity and result interpretation policy. | Limitations table. |

## Baseline Section Evidence

| baseline | Chapter 5 evidence | Chapter 6 later evidence |
| --- | --- | --- |
| rate_based | implemented controller, implementation spec, API mapping, unit tests for bytes/s safe throughput, conservative upshift, aggressive downshift, low-buffer guard and forbidden-signal boundaries. | Later benchmark methodology; current fake smoke is integration validation only. |
| bba | implemented controller, implementation spec, API mapping, unit tests for reservoir/cushion thresholds, intermediate mapping, monotonicity, invalid buffers, bytes/s output and forbidden throughput/text/network boundaries. | Later benchmark methodology; current fake smoke is integration validation only. |
| bola | implemented controller, implementation spec, API mapping, unit tests for BOLA score computation, low/higher buffer behavior, exact/approx segment sizes, no-throughput requirement, parameter defaults and forbidden-signal boundaries. | Later benchmark methodology; current fake smoke is integration validation only. |
| mpc | implemented controller, implementation spec, API mapping, unit tests for harmonic prediction, horizon enumeration, buffer simulation, rebuffer/switching penalties, first-action behavior, bytes/s output and forbidden-signal boundaries. | Later benchmark methodology; current fake smoke is integration validation only and the internal objective is not final QoE. |
| robust_mpc | implemented controller, implementation spec, API mapping, unit tests for zero-error equivalence, high-error conservatism, startup safety factor, prediction/error alignment, first-action behavior, bytes/s output and forbidden Pensieve/RL boundaries. | Later benchmark methodology; current fake smoke is integration validation only and there is no Pensieve claim. |

## Figures To Create Later

- Client module architecture.
- Controller feedback and decision loop.
- Documentation-to-code validation gate.
- Fake-engine validation path.
- Baseline family and implementation order.
- MPC and RobustMPC decision flow.

## Tables To Create Later

- Controller API signal mapping summary.
- Baseline implementation order.
- Unit test categories by controller.
- Smoke scenario matrix.
- Metric validity classification.
- Limitations and deferred methodology.

## Traceability Rule

Every implementation subsection should cite a local Markdown evidence document before citing code. Code explains how the project implements the decision; science docs explain why that implementation is legitimate.
