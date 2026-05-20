# Mahimahi Or Alternatives

Mahimahi is a mandatory Phase 3 source because it is a recognized record-and-replay system for HTTP experiments. It is not automatically the implementation choice for DashClientModular4.

## Comparison

| method | strengths | risks | best Phase 3 use |
| --- | --- | --- | --- |
| Mahimahi | Published HTTP record-and-replay methodology; useful credibility for repeatable web experiments. | Linux-oriented setup, external dependency, possible mismatch with the current fake engine path, extra operational cost. | Method card and possible future external validation. |
| Linux `tc/netem` | Standard Linux traffic-control emulation; can model delay, loss, reordering and rate effects. | Requires Linux networking privileges; trace-driven throughput shaping may need extra tooling; less direct for deterministic unit tests. | Fallback or complementary method for system-level emulation. |
| Custom fake trace-driven runner | Fits Python tests; can be deterministic; can avoid root privileges and media downloads; aligns with fake engine path. | Must be carefully specified to avoid becoming an unrealistic simulator or hidden QoE implementation. | Primary likely implementation candidate for reproducible Phase 3 tests. |

## Selection Criteria

1. Prefer the method that can be validated with synthetic traces first.
2. Prefer deterministic execution for automated tests.
3. Prefer no controller, player, media-engine or metric changes.
4. Prefer raw data and run outputs outside the repository.
5. Prefer a method whose limitations can be explained in Chapter 6.
6. Use external emulation only when it adds scientific value that the fake runner cannot provide.

## Non-Decision

Phase 3.1 does not:

- install Mahimahi;
- configure `tc/netem`;
- implement a fake trace-driven runner;
- run GStreamer benchmarks;
- rank controller performance.

