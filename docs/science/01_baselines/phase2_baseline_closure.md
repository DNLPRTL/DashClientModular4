# Phase 2 Baseline Closure

## Closure Verdict

Phase 2 is complete at the baseline implementation and documentation level. DashClientModular4 now has the mandatory ABR baseline set selected, documented, implemented, registered, unit-tested and validated through fake-engine integration checks, while still preserving the Phase 1 boundary: no final QoE/reward, no replay/traces/emulation, no benchmark ranking and no AI/RL controller have been introduced.

This document is a formal closure statement. It does not introduce controller code, alter controller algorithms, change player/runtime behavior, modify media engines or define evaluation metrics.

## Phase 2 Objective

Phase 2 turns the Phase 1 ABR-neutral client into a scientifically traceable baseline platform. The objective was to select a defensible initial ABR baseline set, convert paper evidence into implementation specifications, implement the mandatory controllers under the existing controller contract, and validate that each controller can run through the client without contaminating future evaluation methodology.

The target was implementation readiness, not benchmark evidence.

## What Was Selected

The selected mandatory Phase 2 baseline set is:

| group | controllers | role |
| --- | --- | --- |
| technical sanity controls | `min_rate`, `fixed_rate`, `max_rate` | validate registry, units, quantization, fake-engine integration and artifacts before academic baselines |
| throughput baseline | `rate_based` | first academic ABR baseline, driven by application-layer throughput |
| buffer baseline | `bba` | academic buffer-occupancy baseline using BBA-0 reservoir/cushion behavior |
| utility/buffer baseline | `bola` | academic BOLA-basic baseline using utility, buffer and segment size |
| planning baseline | `mpc` | academic small-horizon enumerative MPC baseline |
| robust planning baseline | `robust_mpc` | academic robust MPC variant with conservative prediction correction |

The selection is grounded in the source inventory, paper cards, source-evidence documents, baseline selection matrix, signal matrix, controller mappings and acceptance matrices under `docs/science/01_baselines/`.

## What Was Implemented

Phase 2 implemented and registered the following canonical controller names:

- `min_rate`
- `fixed_rate`
- `max_rate`
- `rate_based`
- `bba`
- `bola`
- `mpc`
- `robust_mpc`

The implementation modules are:

- `core/controller/sanity_rate.py`
- `core/controller/rate_based.py`
- `core/controller/bba.py`
- `core/controller/bola.py`
- `core/controller/mpc.py`
- `core/controller/robust_mpc.py`

The registry surface is documented in `baseline_registry_audit.md` and exposed by `core/controller/registry.py`. The implementations follow the current dict-based controller API, return target rates in bytes per second, and use representation indices as quality levels.

## What Was Not Implemented

| method | Phase 2 status | reason |
| --- | --- | --- |
| SODA | documented modern optional candidate, not implemented | useful future non-neural method, but outside the mandatory baseline set and dependent on later methodology |
| RBC | backup optional candidate, not implemented | source identity and value must be locked before any promotion |
| Pensieve | historical IA/RL reference only, not implemented | requires reward, training, model handling, traces/simulator methodology and an AI/RL phase |
| DYNAMIC | deferred practical dash.js-derived method | production hybrid behavior would blur the initial academic baseline comparison |
| FAST SWITCHING | deferred practical dash.js-derived method | segment replacement behavior may affect runtime semantics and is not needed for Phase 2 closure |
| replay/traces/emulation | not built | belongs to Phase 3 methodology |
| final QoE/reward | not defined | belongs to later evaluation methodology |
| benchmark ranking | not claimed | requires trace/replay/emulation and final metric policy |

## What Tests Validate

Controller unit tests validate deterministic decision behavior, contract compatibility, target-rate units, representation-index handling, ladder bounds, edge-case fallback behavior and forbidden-signal boundaries. The registry audit validates canonical names, legacy/debug preservation and constructor compatibility without final QoE or reward objects.

Config/import tests and `py_compile` validate that controller modules are importable and syntactically valid in the current client. Strict readiness validates that Phase 1 neutrality and artifact contracts remain intact after the controller work.

These tests validate implementation correctness at the contract and invariant level. They do not validate performance.

## What Smoke Validates

Fake-engine smoke validation checks that controllers integrate through configuration, registry creation, player feedback, controller action, quantization and canonical artifact production.

Smoke fake is integration validation, not benchmark evidence. It does not compare algorithms, does not define final QoE/reward, does not prove paper-level performance, and does not make GStreamer timing benchmark-grade.

## What Is Not Benchmark Evidence

The following are explicitly not benchmark evidence in Phase 2:

- unit-test pass counts;
- fake-engine smoke runs;
- readiness checks;
- GStreamer integration/demo runs;
- generated runtime CSVs from smoke validation;
- internal MPC or RobustMPC objective terms;
- controller-local debug metrics.

Phase 2 can claim that the mandatory baselines are implemented, registered, tested and integration-ready. It cannot claim QoE superiority, real-network generalization, trace replay validity, AI/RL comparison or final benchmark ranking.

## Why Phase 2 Is Complete

Phase 2 is complete because:

- the mandatory controller set has been selected and documented;
- each academic controller has paper/source evidence, implementation spec, API mapping, acceptance tests and memory notes;
- the sanity controllers and academic baselines are implemented under canonical registry names;
- controller-specific unit tests cover formulas, invariants and forbidden-signal boundaries;
- registry, config/import, syntax and strict-readiness checks cover integration compatibility;
- fake smoke evidence is documented with the correct non-benchmark interpretation;
- optional and deferred methods are explicitly bounded;
- all known limitations are declared before evaluation starts.

This closes the baseline implementation phase without entering evaluation methodology.

## What Phase 3 Must Do Next

Phase 3 must define the trace, replay and emulation methodology before any final benchmark claims are made. The next phase should:

- choose trace datasets and document their provenance;
- decide whether replay, network emulation or both are required;
- evaluate Mahimahi and alternative emulation/replay options;
- define reproducible network scenarios;
- connect traces to the fake/replay architecture without changing controller semantics unfairly;
- decide train/test/OOD splits if IA/RL work later requires them;
- avoid train/test leakage;
- keep final QoE/reward and ranking claims deferred until the methodology is complete.

Phase 2.4 does not implement any of those Phase 3 items.
