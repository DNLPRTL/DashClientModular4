# Phase 3 Defense Talking Points

## Core Position

Phase 3 exists because implemented ABR controllers cannot be compared scientifically without reproducible network conditions. The project therefore documents trace discovery, dataset selection, replay/emulation decisions and leakage controls before running benchmarks.

## Strong Answers

- The Phase 2 controllers are already implemented and validated as code, but not ranked.
- Phase 3 keeps controllers frozen and focuses on the environment around them.
- No dataset is downloaded into the repository; the project records provenance and selection criteria first.
- Puffer is valuable for methodology and statistical caution, but full raw Puffer data is deferred.
- FCC Measuring Broadband America is a broadband reference, not a replay input yet.
- Norway HSDPA is mandatory to card because it is classic, small and ABR-relevant.
- Modern 4G/5G datasets are likely OOD or generalization candidates.
- Lancaster traces are promising for live/HAS realism, subject to carding and terms.
- Mahimahi is a credible method reference, while a custom fake trace-driven runner may be more practical for deterministic Python tests.

## Boundary Statements

- No final QoE/reward is defined in Phase 3.1.
- No replay runner is implemented in Phase 3.1.
- No controller, player, media engine or metric definition changes are made.
- No GStreamer benchmark is claimed.
- No IA/RL work is introduced.

## Likely Questions

| question | answer direction |
| --- | --- |
| Why not use real network tests directly? | They are hard to reproduce and confound controller behavior with uncontrolled network variation. |
| Why not use only Mahimahi? | It is credible, but may be operationally heavier than needed for deterministic local Python tests. It remains a candidate. |
| Why keep Puffer raw data deferred? | It is large and statistically subtle; Phase 3.1 only records metadata and caution. |
| How do you avoid overfitting traces? | Split policy, OOD separation, synthetic development traces and parameter freeze rules. |
| When can controllers be ranked? | Only after trace/replay methodology, final QoE/reward and result interpretation are closed. |

## Phase 3.2A Source-Triage Update

Use these talking points after the source cards are added:

- Phase 3.2A intentionally does not implement code because dataset and replay choices must be defensible first.
- The first implementation should prioritize determinism and testability through a custom Python trace-driven fake/replay runner.
- Mahimahi and `tc/netem` are considered, carded and kept as candidates, but are not forced prematurely.
- CausalSim and Veritas are included as threats-to-validity references, not implementation targets.
- Puffer warns against overclaiming from trace-driven tests because real deployment effects and causal bias matter.
- No dataset becomes final benchmark material and no final split is closed in Phase 3.2A.

## Phase 3.2B Schema Update

Use these talking points after the common schema is defined:

- The common schema uses `timestamp_s`, `duration_s` and `throughput_kbps` so every dataset must pass through the same unit boundary.
- `throughput_kbps = 0` is allowed for outage/no-delivery intervals, but missing throughput is not silently treated as zero.
- The future runner must not expose future trace samples directly to controllers.
- Raw and normalized real traces stay outside the repository.
- HSDPA, Ghent and Lancaster are conversion priorities, not final benchmark material.
- Raca 5G and Lumos5G are held as OOD candidates for future generalization work.
- Phase 3.2B prepares trace inputs; Phase 3.5 still has to close QoE/reward.
