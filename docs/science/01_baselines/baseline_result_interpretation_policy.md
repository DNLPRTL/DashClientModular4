# Baseline Result Interpretation Policy

This policy prevents implementation checks from being mistaken for benchmark evidence.

## Evidence Ladder

| evidence | validates | does not validate |
| --- | --- | --- |
| Unit tests | Formula logic, edge cases, contract behavior. | Runtime integration or performance. |
| Fake smoke tests | Controller integration, canonical artifacts, deterministic path. | Final QoE, paper-level performance, real-network superiority. |
| Client readiness | Existing architecture neutrality and output hygiene remain intact. | Controller scientific superiority. |
| Future trace/replay | Scenario reproducibility under defined traces. | Final comparison unless QoE/reward is defined. |
| Future final QoE/reward | Academic comparison under approved methodology. | Out-of-scope methods not included in the protocol. |

## Interpretation Rules

1. A passing unit test means the decision logic matches the documented fixture.
2. A passing fake smoke run means the controller integrates with the client path.
3. A passing readiness script means the client still satisfies Phase 1 neutrality constraints.
4. `use_for_eval=true` marks candidate rows for later evaluation, not final scoring.
5. Paper-level claims require later Phase 3/3.5/6 methodology, not Phase 2.3 smoke tests.

## Allowed Phase 2.3 Statements

- "`rate_based` passed its unit tests for safe throughput selection."
- "`bba` selected the minimum rate below the reservoir in a fake smoke scenario."
- "`bola` ran without DYNAMIC or FAST SWITCHING features."
- "`mpc` returned the first action of the best internal-score sequence in unit fixtures."
- "`robust_mpc` became more conservative when recent prediction error was high."

## Forbidden Phase 2.3 Statements

- "`bola` is better than `bba`."
- "`mpc` improves QoE."
- "`robust_mpc` reproduces Pensieve paper performance."
- "Fake-engine smoke tests are benchmark results."
- "GStreamer validates real playback QoE."
- "The produced CSVs are final training data."

## Escalation To Benchmark Claims

Before any comparative claim, the project must have:

- final scenario methodology;
- final QoE/reward definition;
- trace/replay or equivalent controlled environment;
- controller parameter freeze;
- artifact interpretation rules;
- limitations and threats to validity.
