# Phase 2 Academic Validity Statement

## Validity Claim

In Phase 2, an academically valid implementation means that a controller is implemented from documented scientific evidence and validated against the local client contract before any performance claim is made.

The validity claim is limited to implementation fidelity, contract compatibility and methodological traceability. It is not a claim of final QoE superiority.

## Required Evidence

For each implemented academic baseline, Phase 2 requires:

- paper-derived source evidence;
- an implementation specification that translates the source into deterministic behavior;
- documented formulas, units, parameters and fallback behavior;
- declared simplifications and exclusions;
- a controller API mapping to available DashClientModular4 signals;
- acceptance tests describing expected invariants;
- unit tests covering formulas, edge cases and forbidden-signal boundaries;
- registry/config/import compatibility;
- fake-engine smoke validation for integration and artifacts;
- memory notes connecting the implementation to the TFG thesis narrative.

## Controller Contract Compatibility

A Phase 2 controller is valid only if it respects the existing client contract:

- target rates are bytes per second;
- quality levels are representation indices;
- representation ladders come from the MPD/client state;
- controllers do not parse MPDs, download segments, write artifacts or define evaluation rows;
- controllers do not depend on console output, `run.log` text, GStreamer-specific internals, future oracles, server-side state, TCP internals or final QoE/reward objects.

## Simplification Policy

Simplifications are allowed only when they are explicit and tested. Phase 2 declares, among others:

- `bba` is BBA-0 style reservoir/cushion behavior, not Netflix production internals;
- `bola` is BOLA-basic, not DYNAMIC, FAST SWITCHING, BOLA-E or full production dash.js behavior;
- `mpc` is small-horizon enumerative MPC, not FastMPC;
- `robust_mpc` is classical robust MPC correction, not Pensieve, RL or neural inference.

## What Phase 2 Proves

Phase 2 proves that the mandatory baseline implementations are:

- selected by documented scope decisions;
- grounded in source-evidence and implementation specs;
- implemented under canonical registry names;
- compatible with the controller contract;
- unit-tested for their intended invariants;
- integrated through fake-engine smoke validation;
- bounded by explicit limitations.

## What Phase 2 Does Not Prove

Phase 2 does not prove:

- final QoE superiority;
- real-network generalization;
- benchmark ranking;
- trace replay validity;
- Mahimahi or alternative emulation validity;
- IA/RL comparison;
- Pensieve reproduction;
- production dash.js equivalence;
- final reward or QoE correctness.

Those claims require later methodology, traces/replay/emulation and a final metric policy.
