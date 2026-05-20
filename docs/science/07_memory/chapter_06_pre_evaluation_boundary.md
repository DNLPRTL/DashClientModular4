# Chapter 06 Pre-Evaluation Boundary

These notes define what can and cannot be evaluated before replay/traces and final QoE methodology exist. They are source material for the future memory, not final LaTeX chapter text.

## What Can Be Evaluated Now

- Controller modules import successfully.
- Registry names resolve to controller objects.
- Controllers return target rates in bytes per second.
- Quantization maps target rates to representation indices.
- Unit fixtures validate documented decision behavior.
- Fake smoke validates integration and canonical artifact production.
- Readiness checks validate that Phase 1 client neutrality remains intact.

## What Cannot Be Claimed Yet

- No final QoE/reward has been defined.
- No replay or trace methodology has been implemented.
- No network emulation methodology has been implemented.
- No real-network benchmark has been run.
- No controller can be ranked against another controller.
- No generated CSV is a final training dataset.
- No GStreamer run is benchmark-grade evidence.

## Evidence Types

| evidence type | validates | does not validate |
| --- | --- | --- |
| unit tests | local decision logic, edge cases, units and forbidden-signal boundaries | integration artifacts or final performance |
| fake smoke | config/registry/client-loop integration and canonical artifacts | algorithm superiority or final QoE |
| readiness check | output hygiene, neutrality and reproducibility contracts | paper-level results |
| replay/traces | later controlled scenario repeatability | final comparison unless QoE/reward is defined |
| final benchmark/QoE | later comparative claims under frozen methodology | methods outside that methodology |

## Why Phase 3 And 3.5 Are Needed

Phase 2.3 gives a stable controller set. It does not yet give an evaluation environment. Phase 3 and Phase 3.5 are needed to define trace/replay/emulation inputs, scenario boundaries, repeatability rules, parameter freezes and artifact interpretation. Only after that can Phase 6 define final QoE/reward and compare controllers formally.

## Defense Boundary

When defending the project before final evaluation, use careful verbs:

- valid now: implemented, registered, unit-tested, contract-compatible, smoke-validated, reproducible;
- not valid yet: outperforms, improves QoE, reproduces paper results, generalizes to real networks, benchmark winner.
