# Replay Emulation Decision

This document defines decision criteria. It does not select or implement a final runner.

## Decision Question

Which mechanism should DashClientModular4 use later to expose the Phase 2 controllers to reproducible network behavior?

## Candidate Mechanisms

| candidate | role | current Phase 3.1 decision |
| --- | --- | --- |
| Mahimahi | Established HTTP record-and-replay method candidate. | Mandatory method card; not mandatory implementation. |
| Linux `tc/netem` | Kernel network emulation candidate. | Mandatory method card; fallback or complementary option. |
| Custom fake trace-driven runner | Deterministic Python-side replay candidate. | Primary likely implementation candidate for reproducible tests, but not implemented in this block. |
| Hybrid approach | Fake runner for tests plus external emulator for selected validation. | Possible later decision. |

## Decision Criteria

| criterion | why it matters |
| --- | --- |
| Reproducibility | Runs must be repeatable across controllers and dates. |
| Controller neutrality | The mechanism must not require controller-specific changes. |
| Python 3.8 compatibility | Future implementation must fit the current project environment. |
| CI/local practicality | The mechanism should work without fragile root/network setup for basic tests. |
| Scientific credibility | Method should be explainable and, where possible, tied to published systems methodology. |
| Trace fidelity | It should preserve time-varying throughput behavior without inventing hidden signals. |
| Platform risk | Windows development and Linux emulation constraints must be explicit. |
| Storage hygiene | Raw traces and run outputs must stay out of git. |
| Artifact clarity | Future runs must produce manifests and summaries that can be interpreted later. |

## Current Likely Direction

The primary likely implementation candidate is a custom fake trace-driven runner because it can support deterministic Python tests and avoid privileged network manipulation. Mahimahi remains important as a method reference and possible external validation tool. `tc/netem` remains a practical Linux fallback for latency/loss/rate emulation when platform constraints allow it.

This is not a final selection. The final decision requires method cards, platform checks and a small synthetic-trace validation plan.

## Final Method Gate

Before implementation, the selected method must have:

1. a completed method card;
2. explicit input trace schema;
3. deterministic clock or scheduling assumptions;
4. artifact contract;
5. leakage controls;
6. platform and dependency notes;
7. confirmation that controllers, player, media engines and metrics remain unchanged.

