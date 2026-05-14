# Python Development Narrative Plan

This is a plan for the future Chapter 4/5 narrative. It is not the final memory chapter.

## Narrative Arc

| step | message | evidence |
| --- | --- | --- |
| Incremental client development | The Python client was built and hardened before ABR claims. | Phase 1 architecture and readiness docs. |
| Architecture before algorithms | Parser, downloader, media engine, controller, logging and evaluation concerns were separated before baseline work. | Architecture audit and baseline entry contract. |
| Contracts before controllers | Units, allowed signals and output artifacts were defined before academic controllers. | `baseline_entry_contract.md` and science mappings. |
| Fake engine for determinism | Fake engine supports controlled implementation checks without real playback timing ambiguity. | Fake smoke protocol and tests. |
| GStreamer boundary | GStreamer demonstrates integration but is not benchmark-grade. | Readiness report and output contract. |
| Controllers one by one | Baselines are added in order: sanity, rate_based, bba, bola, mpc, robust_mpc. | Baseline implementation plan. |
| Tests prove correctness | Unit tests prove formula and edge-case behavior; smoke tests prove integration. | Unit and fake smoke protocols. |
| Artifacts support reproducibility | Canonical outputs capture config, environment, logs and telemetry. | Output artifact contract. |
| Commit history supports traceability | Each major change has its own commit and docs. | Git history and source inventories. |

## Suggested Chapter Sections

1. Client architecture and module boundaries.
2. Controller contract and feedback units.
3. Documentation-first ABR implementation methodology.
4. Deterministic testing with fake engine.
5. Canonical artifacts and reproducibility.
6. Implementation order for academic baselines.
7. Limitations and deferred benchmark methodology.

## Tone For The Memory

Explain the Python work as engineering discipline in service of scientific validity. Avoid presenting the client as a production player or the smoke tests as benchmark evidence.

## Defense Angle

The student should be able to say: "I did not start by coding ABR algorithms. I first made the client testable and neutral, then documented how each paper maps to this client, and only then prepared implementation gates."
