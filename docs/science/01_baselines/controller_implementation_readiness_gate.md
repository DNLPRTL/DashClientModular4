# Controller Implementation Readiness Gate

This gate must pass before coding any Phase 2.3 controller. It is documentation-only and does not authorize benchmark claims.

## Global Gate

| item | requirement | evidence |
| --- | --- | --- |
| Paper card | `paper_card.md` exists for academic baselines | baseline folder |
| Source evidence | `source_evidence.md` exists for academic baselines | baseline folder |
| Implementation spec | `implementation_spec.md` exists | baseline folder |
| Controller API mapping | `controller_api_mapping.md` exists | baseline folder |
| Acceptance tests | `acceptance_tests.md` exists | baseline folder |
| Memory notes | `notes_for_memory.md` exists | baseline folder |
| Controller contract | `docs/architecture/baseline_entry_contract.md` reviewed | target rates are bytes per second; levels are representation indices |
| Telemetry requirements | `baseline_signal_matrix.md` and telemetry provenance reviewed | no invented signal without provenance |
| Unit-test plan | controller-specific acceptance tests reviewed | future `unittest`, not `pytest` |
| Fake smoke scenario | fake-engine smoke scenario reviewed | implementation validation only |
| QoE boundary | no final QoE/reward required | internal controller objective allowed only where specified |
| Benchmark boundary | no benchmark claim allowed | smoke tests are not paper-level results |

## Per-Controller Checklist

| controller | paper_card | source_evidence | implementation_spec | mapping | acceptance_tests | notes_for_memory | extra gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sanity_controllers | N/A, local sanity specs | N/A | `fixed_rate_spec.md`, `min_rate_spec.md`, `max_rate_spec.md` | local contract review | `sanity_controllers/acceptance_tests.md` | `sanity_controllers/notes_for_memory.md` | Must be labeled test/sanity only, never academic baseline. |
| rate_based | required | required | required | required | required | required | Throughput from application-layer segment size/time only; no TCP RTT/loss. |
| bba | required | required | required | required | required | required | Buffer level is primary signal; throughput guard is optional/deferred. |
| bola | required | required plus dash.js practical evidence | required | required | required | required | Must be BOLA-basic; no DYNAMIC, FAST SWITCHING or BOLA-E. |
| mpc | required | required | required | required | required | required | Internal objective is controller-only and not final evaluation QoE. |
| robust_mpc | required plus Pensieve artifact card | required | required | required | required | required | Must not implement Pensieve, RL, neural inference or training. |

## Pass/Fail Rule

A controller may enter implementation only when every required document exists, the allowed signals are explicitly mapped, and its acceptance tests are precise enough to become future unit tests or fake smoke checks.

If a controller needs a new runtime signal, output field, config key, or metric interpretation, implementation stops until the docs explain the need and a separate code block is approved.

## What This Gate Does Not Do

- It does not implement controllers.
- It does not create code tests.
- It does not define final QoE/reward.
- It does not create traces, replay, emulation, datasets, or benchmark code.
- It does not allow comparing algorithms as better or worse.
