# Baseline Implementation Summary

Phase 2.3 closes the mandatory baseline implementation set for DashClientModular4. This summary is an audit artifact: it describes what is implemented and registered at HEAD `504f48f`, without adding new controller algorithms or benchmark claims.

| controller | type | source/status | implementation module | test module | registered name | primary decision signal | target_rate unit | quality_level unit | implementation status | commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `min_rate` | technical sanity controller | local sanity spec; not academic | `core/controller/sanity_rate.py` | `tests/test_sanity_rate_controllers.py` | `min_rate` | MPD/client ladder minimum | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `fixed_rate` | technical sanity controller | local sanity spec; not academic | `core/controller/sanity_rate.py` | `tests/test_sanity_rate_controllers.py` | `fixed_rate` | configured level or target rate clamped to ladder | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `max_rate` | technical sanity controller | local sanity spec; not academic | `core/controller/sanity_rate.py` | `tests/test_sanity_rate_controllers.py` | `max_rate` | MPD/client ladder maximum allowed by `max_level` | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `rate_based` | academic ABR baseline | mandatory throughput baseline implemented in Phase 2.3.2 | `core/controller/rate_based.py` | `tests/test_rate_based_controller.py` | `rate_based` | application-layer throughput estimate with safety factor and low-buffer guard | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `bba` | academic ABR baseline | mandatory buffer baseline implemented in Phase 2.3.3 | `core/controller/bba.py` | `tests/test_bba_controller.py` | `bba` | `queued_time` reservoir/cushion buffer map | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `bola` | academic ABR baseline | mandatory utility-buffer baseline implemented in Phase 2.3.4 | `core/controller/bola.py` | `tests/test_bola_controller.py` | `bola` | BOLA-basic utility/buffer/segment-size score | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `mpc` | academic ABR baseline | mandatory hybrid planning baseline implemented in Phase 2.3.5 | `core/controller/mpc.py` | `tests/test_mpc_controller.py` | `mpc` | harmonic throughput prediction, buffer simulation and internal sequence objective | `bytes_per_second` | `representation_index` | implemented and registered | present at `504f48f` |
| `robust_mpc` | academic ABR baseline | mandatory robust planning baseline implemented in Phase 2.3.6 | `core/controller/robust_mpc.py` | `tests/test_robust_mpc_controller.py` | `robust_mpc` | MPC planner with conservative prediction-error correction | `bytes_per_second` | `representation_index` | implemented and registered | `504f48f` |

## Scope Distinctions

- `min_rate`, `fixed_rate` and `max_rate` are technical sanity controllers. They validate registry, controller contract, ladder quantization, fake-engine integration and artifact plumbing; they are not academic ABR baselines.
- `rate_based`, `bba`, `bola`, `mpc` and `robust_mpc` are the mandatory academic ABR baselines implemented for Phase 2.3.
- SODA remains an optional candidate and is not implemented.
- Pensieve remains a historical and IA/RL reference for context and comparison. It is not implemented.
- BOLA DYNAMIC and FAST SWITCHING behavior remain deferred. The implemented controller is BOLA-basic only.

## Closure Meaning

The implementation summary supports the claim that the mandatory controller set exists, is registered and has dedicated unit coverage. It does not support final QoE, replay, trace, real-network or benchmark superiority claims.
