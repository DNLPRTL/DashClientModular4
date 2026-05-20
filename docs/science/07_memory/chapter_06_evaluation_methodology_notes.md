# Chapter 06 Evaluation Methodology Notes

These notes extend the pre-evaluation boundary with Phase 3 trace/replay methodology. They are not final LaTeX prose.

## Chapter Role

Chapter 6 should explain the evaluation ladder:

1. Phase 1 client readiness and output hygiene.
2. Phase 2 controller implementation and unit/fake-smoke validation.
3. Phase 3 trace, replay, emulation and dataset methodology.
4. Later final QoE/reward and benchmark ranking.

## Phase 3 Message

The key message is that a DASH ABR comparison needs controlled network conditions before performance claims are meaningful. Phase 3 therefore documents dataset provenance, replay/emulation choices, train/test/OOD boundaries, leakage prevention and future artifact expectations.

## What Phase 3.1 Adds

- Source inventory for trace/replay literature and datasets.
- Dataset selection criteria.
- Replay/emulation decision criteria.
- Mahimahi, `tc/netem` and fake-runner comparison.
- Split and OOD policy.
- Leakage prevention policy.
- Synthetic trace plan.
- Run artifact expectations.

## What Remains Deferred

- dataset downloads;
- replay implementation;
- final QoE/reward;
- benchmark ranking;
- IA/RL;
- controller/player/media/metric changes;
- GStreamer benchmark claims.

## Defense Wording

Use careful verbs: documented, scoped, classified, deferred, selected as candidate, requires carding, requires later validation.

Avoid: proved, outperformed, reproduced, optimized, trained, deployed, benchmarked.

## Phase 3.2A Source-Triage Update

Chapter 6 can now cite the Phase 3.2A card set and triage matrix as methodology evidence, not as experimental results.

New material available:

- dataset selection rationale table;
- replay/emulation method comparison table;
- threats to validity: exogenous trace assumption, log-derived trace bias, split leakage, storage risk and format risk;
- OOD/generalization policy;
- explanation that unit tests, smoke tests and fake traces are not benchmark evidence.

Important wording:

- first integration candidates: HSDPA Norway, Ghent 4G/LTE and Lancaster HAS traces;
- modern mobile/OOD candidates: Raca 4G, Raca 5G and Lumos5G;
- reference-only: FCC Measuring Broadband America;
- metadata-only: Puffer data archive;
- primary likely implementation path: custom Python trace-driven fake/replay runner, not implemented in Phase 3.2A;
- secondary validation candidate: Mahimahi;
- Linux fallback candidate: `tc/netem`;
- threats-to-validity references: CausalSim and Veritas.
