# Baseline Registry Audit

This audit verifies the Phase 2.3 registry surface at HEAD `504f48f`. The registry remains the only supported way for configuration names to resolve to controller objects.

## Registered Names

| registered name | factory class | status | intended use |
| --- | --- | --- | --- |
| `min_rate` | `MinRateController` | implemented | technical sanity/control |
| `fixed_rate` | `FixedRateController` | implemented | technical sanity/control |
| `max_rate` | `MaxRateController` | implemented | technical sanity/control |
| `rate_based` | `RateBasedController` | implemented | academic throughput baseline |
| `bba` | `BbaController` | implemented | academic buffer baseline |
| `bola` | `BolaController` | implemented | academic BOLA-basic baseline |
| `mpc` | `MpcController` | implemented | academic hybrid planning baseline |
| `robust_mpc` | `RobustMpcController` | implemented | academic robust planning baseline |
| `fixed_quality` | `FixedQualityController` | preserved | test/debug legacy support |
| `scripted_quality` | `ScriptedQualityController` | preserved | test/debug legacy support |
| `max_quality` | `MaxQualityController` | preserved | legacy/debug/stress support |

No Phase 2.3 controller was silently renamed. The canonical academic names are lower-case, underscore-separated config keys.

## Contract Expectations

- `target_rate` is bytes per second.
- `quality_level` is a representation index.
- The representation ladder comes from MPD/client state through `rates` and `max_level`.
- Controllers receive player feedback through the current dict-based API.
- Controllers do not parse MPDs, download segments, write CSV files, change `eval_phase`, define `use_for_eval`, or mutate benchmark contracts.
- Controllers must not depend on console output, progress labels, `run.log` text or GStreamer-specific events as decision inputs.
- The fake engine is the controlled path for implementation smoke validation.
- GStreamer remains integration/demo evidence, not benchmark-grade evidence.

## Registry Checklist

| item | status | evidence |
| --- | --- | --- |
| registry imports all implemented controllers | pass | `core/controller/registry.py` imports sanity, rate-based, BBA, BOLA, MPC and RobustMPC classes |
| canonical names resolve through `create_controller` | pass | controller-specific unit tests and `tests/test_baseline_registry_audit.py` |
| legacy/debug names remain available | pass | `fixed_quality`, `scripted_quality` and `max_quality` remain in `CONTROLLER_REGISTRY` |
| config/import tests include implemented controllers | pass | `tests/test_config.py` and `tests/test_imports.py` cover all Phase 2.3 modules/names |
| no old controller broken by Phase 2.3 additions | pass | existing debug/legacy creation tests still run in unittest discovery |
| no silent rename | pass | registry keys match `ControllerSpec.key` values |
| no final QoE/reward required by registry | pass | constructors are creatable from config params and do not require final reward objects |

## Boundary

The registry audit proves controller availability and contract compatibility. It does not prove algorithm performance, trace robustness, final QoE validity, replay validity or real-network superiority.

## Phase 2.4 Formal Closure Pointer

Registry evidence is summarized in the formal Phase 2 closure package through `phase2_baseline_closure.md` and `phase2_controller_inventory.md`.
