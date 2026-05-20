# Practical source evidence â€” BOLA, BOLA-E, DYNAMIC, FAST SWITCHING and dash.js

Phase: 2.2A â€” PDF-grounded source evidence  
Related baseline: `bola`  
Primary practical source: Spiteri, Sitaraman, Sparacio, "From Theory to Practice: Improving Bitrate Adaptation in the DASH Reference Player", ACM TOMM 2019.  
Status: practical evidence layer only. Not an implementation spec and not runtime code.

## Purpose

This document captures the practical implementation lessons from the DASH reference player paper. It prevents us from overclaiming that a simple BOLA implementation equals production dash.js behavior.

Phase 2.3.4 status: DashClientModular4 implements `bola` as BOLA-basic only. This practical evidence remains a boundary note: DYNAMIC, FAST SWITCHING, BOLA-E, live low-latency behavior and full dash.js production behavior are not implemented.

## Role in the TFG

This source is not a separate mandatory baseline. It is an auxiliary source for:
- BOLA implementation caveats;
- dash.js practical behavior;
- DYNAMIC and FAST SWITCHING as deferred optional methods;
- explaining why production ABR has additional engineering constraints.

## Evidence extracted from Spiteri 2019

### Real-world ABR requirements

The paper states that practical ABR algorithms must provide:
- high sustainable bitrate;
- low rebuffering;
- low bitrate oscillations;
- responsiveness to startup, seek and network changes;
- usability in demanding scenarios such as low-latency live streaming.

Operational consequence:
- Our BOLA-basic implementation must not be claimed as production-grade.
- Acceptance tests must check deterministic behavior and safe fallback, not production QoE.

### BOLA limitations in production

The paper reports that BOLA alone can be slow to respond to startup/seek events and rapid throughput changes because it predominantly uses buffer level. It also has issues in small-buffer live scenarios.

Operational consequence:
- The initial TFG implementation should be explicit: "BOLA-basic, not BOLA-E/DYNAMIC".
- Low-latency/live behavior is out of scope for the first baseline implementation.

### BOLA-E

BOLA-E enhances BOLA using:
- placeholder/virtual segment mechanism;
- insufficient buffer rule;
- improved responsiveness and lower rebuffering risk when buffer levels are low.

Operational consequence:
- Do not implement BOLA-E in the first BOLA baseline.
- Mention as future optional refinement.
- The BOLA evidence may include a safety guard inspired by insufficient-buffer reasoning only if clearly documented as simplification, not BOLA-E.

### DYNAMIC

DYNAMIC uses throughput-based selection when the buffer level is low and switches to BOLA when buffer levels are sufficiently high. It switches back to throughput mode when buffer falls below threshold and BOLA would choose lower than throughput.

Evidence-level operational summary:
```text
low buffer -> throughput-based mode
higher buffer -> BOLA mode
```

The paper describes a 10-second buffer threshold in its dash.js DYNAMIC discussion.

Operational consequence:
- Do not implement DYNAMIC initially.
- DYNAMIC may be documented in optional candidates as a future hybrid method.
- `rate_based` + `bola` implemented separately first will make DYNAMIC easier later.

### THROUGHPUT rule

The paper describes a simple throughput heuristic:
- estimate throughput using a sliding-window primitive;
- pick the highest encoded bitrate lower than a safety factor of the estimated throughput;
- the paper mentions a 90% safety factor in the DYNAMIC section.

Operational consequence:
- This supports using a safety factor in `rate_based`.
- It does not replace Liu 2011 as the primary source for `rate_based`.

### FAST SWITCHING

FAST SWITCHING replaces already-buffered lower-bitrate segments with higher-bitrate segments when improved connectivity makes it possible.

Operational consequence:
- Do not implement FAST SWITCHING initially.
- It interacts with scheduling/buffer replacement and is not a pure controller decision.
- It belongs to future work, not initial baseline implementation.

### Sabre

Sabre is a simulator designed to test ABR algorithms with an architecture similar to dash.js. It uses:
- network trace;
- video description/manifest-like data;
- segment length;
- bitrate ladder;
- segment size matrix;
- ABR algorithm input/output;
- QoE metrics.

Operational consequence:
- Useful for future replay/benchmark design.
- Do not create replay/benchmark code in 2.2A or 2.2B.
- Fake engine remains the controlled path for current smoke tests.

### dash.js architecture

The paper describes how dash.js uses:
- ScheduleController for segment download scheduling;
- abrController for bitrate choice;
- ABR rules such as ThroughputRule and BolaRule;
- BufferController/MSE integration.

Operational consequence:
- In DashClientModular4, controllers must remain inside the existing controller contract.
- Do not import dash.js architecture directly.
- Do not let controller decisions depend on console output.

## Required operational decisions for Phase 2.2B

- `bola` implementation spec must say "BOLA-basic".
- `bola` acceptance tests must not test DYNAMIC or FAST SWITCHING.
- `bola` notes_for_memory must mention production limitations.
- `optional_candidates.md` may mention DYNAMIC and FAST SWITCHING as deferred ideas, but they are not initial baselines.
- `rate_based` may use a safety factor, but its primary source remains Liu 2011.

## What this source does not justify

- It does not justify replacing BOLA with DYNAMIC.
- It does not justify implementing FAST SWITCHING before core baselines.
- It does not justify making GStreamer benchmark-grade.
- It does not justify final QoE/reward.
- It does not justify importing dash.js code.

## Use in memory

Chapter 2:
- Mention dash.js as practical reference player context.

Chapter 5:
- Explain BOLA-basic limitations and why DYNAMIC/FAST SWITCHING are deferred.

Chapter 6:
- Later, if relevant, list practical implementation limitations and threats to validity.

Suggested table:
- BOLA-basic vs BOLA-E vs DYNAMIC vs FAST SWITCHING: included/deferred/why.

Suggested figure:
- own diagram: low-buffer throughput mode vs high-buffer BOLA mode for DYNAMIC, marked as deferred.
