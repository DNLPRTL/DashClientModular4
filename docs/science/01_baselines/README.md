# Baseline Selection

This folder defines the Phase 2 ABR baseline selection scaffold.

It is documentation-only. It does not implement rate-based, BBA, BOLA, MPC, RobustMPC, SODA, Pensieve, DYNAMIC, FAST SWITCHING, replay, traces, QoE reward, datasets, or benchmark code.

## Initial Baseline Set

| order | controller class | status |
| --- | --- | --- |
| 1 | sanity controllers: `min_rate`, `fixed_rate`, `max_rate` | document first, then use for plumbing sanity only |
| 2 | `rate_based` | mandatory later academic baseline |
| 3 | `bba` | mandatory later academic baseline |
| 4 | `bola` | mandatory later academic baseline |
| 5 | `mpc` | mandatory later academic baseline |
| 6 | `robust_mpc` | mandatory later academic baseline |
| 7 | optional candidates | only if later justified |

## Required Gate Before Code

For every academic baseline implementation, create and review:

- `paper_card.md`
- `implementation_spec.md`
- `controller_api_mapping.md`
- `acceptance_tests.md`
- `notes_for_memory.md`

The current block creates paper/source cards and templates. It intentionally does not create full implementation specs for the mandatory academic baselines.
