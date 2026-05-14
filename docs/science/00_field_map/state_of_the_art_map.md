# State of the Art Map

## Scope

The TFG focuses on client-side HTTP Adaptive Streaming and MPEG-DASH ABR logic. The implementation target is a controlled, modular DASH client prepared for reproducible experiments, with the fake engine as the benchmark-grade path.

## Core Axes

| axis | categories | relevance to TFG |
| --- | --- | --- |
| Adaptation signal | throughput, buffer, hybrid, optimization, learning-based | Defines baseline families and required telemetry. |
| Control location | client-side, server-assisted, CDN-assisted, network-assisted | Initial scope is client-side only. |
| Evaluation mode | fake engine, replay/traces, emulation, live integration | Initial controlled path is fake engine; replay/traces are deferred. |
| Objective | quality, rebuffering, switching, latency, fairness, energy | Final QoE/reward is deferred; early docs keep dependencies explicit. |
| Implementation maturity | sanity controller, academic baseline, production-derived method, neural/RL | Phase 2 starts with sanity and classic academic baselines. |

## Baseline Families

| family | selected examples | Phase 2 status |
| --- | --- | --- |
| Sanity controllers | min_rate, fixed_rate, max_rate | Document now; useful for smoke tests and instrumentation sanity. |
| Throughput/rate-based | Liu et al. 2011 | Mandatory later baseline. |
| Buffer-based | BBA, BOLA | Mandatory later baselines. |
| MPC/optimization | MPC, RobustMPC | Mandatory later baselines after QoE dependencies are controlled. |
| Hybrid production methods | dash.js DYNAMIC, FAST SWITCHING | Deferred; not initial baselines. |
| Modern non-neural methods | SODA | Optional future candidate only. |
| Neural/RL | Pensieve | Historical reference only in Phase 2; no RL implementation. |

## Current Gap

The client is ready as an ABR-neutral platform, but the scientific layer must define:

- Which baselines are fair to compare.
- Which signals each baseline needs.
- Which signals already exist or can be derived without runtime changes.
- Which QoE assumptions are still open.
- Which paper-derived requirements must be documented before code begins.

## Position

The initial implementation path should favor classic, interpretable baselines whose decisions can be tested under deterministic fake-engine conditions. This keeps the TFG scientifically comparable without jumping early into neural controllers, trace replay, or production-specific hybrid behavior.
