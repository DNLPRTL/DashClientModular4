# Source evidence â€” SODA optional candidate

Phase: 2.2A â€” PDF-grounded source evidence  
Optional method: `soda`  
Primary source: Chen et al., "SODA: An Adaptive Bitrate Controller for Consistent High-Quality Video Streaming", SIGCOMM 2024.  
Status: optional candidate evidence only. Not an implementation spec and not runtime code.

## Purpose

This document captures why SODA is the best modern non-neural optional candidate discovered in Phase 2, while preserving the decision not to implement it initially.

## Paper role in the TFG

SODA is a recent, strong, non-neural ABR controller. It is useful for:
- showing awareness of current research;
- demonstrating that the baseline set was not chosen blindly;
- motivating future extensions beyond BOLA/MPC/RobustMPC.

It is not part of the initial implementation order.

## Evidence extracted from Chen 2024

### Problem addressed

SODA targets frequent bitrate switching, especially in live streaming with short buffers. The paper argues that users can be frustrated by visual-quality inconsistency over time and that live streaming is harder because buffer lengths are smaller.

Operational consequence:
- SODA is relevant to smoothness and short-buffer robustness.
- It is more advanced than the initial baseline set.
- It is not necessary for first classical baseline implementation.

### Main approach

SODA stands for Smoothness Optimized Dynamic Adaptive controller. It uses a framework inspired by smoothed online convex optimization (SOCO) to balance:
- video quality;
- rebuffering/sustained playback;
- bitrate switching/smoothness.

Operational consequence:
- SODA belongs to modern control/optimization ABR, not RL.
- It is non-neural but mathematically more complex than BBA/BOLA/MPC.
- It is a candidate for future optional implementation if time remains.

### Robustness and deployability

The paper emphasizes:
- robustness against throughput prediction errors;
- efficient horizon planning in polynomial time;
- practical deployment within Amazon Prime Video;
- reduction of bitrate switching in production experiments.

Operational consequence:
- SODA is strong enough to cite as modern optional candidate.
- It should not be implemented before the mandatory classical baselines.
- It would require its own implementation spec later if selected.

### Comparison against baselines

The paper compares SODA against relevant baselines such as BOLA, Dynamic and MPC, and discusses limitations of RobustMPC under certain objectives.

Operational consequence:
- SODA can be positioned as a future comparator after BOLA/MPC/RobustMPC are working.
- Its presence strengthens the literature review and candidate matrix.

## Required signals if implemented later

Likely required signals:
- bitrate ladder;
- buffer level;
- throughput prediction or history;
- previous selected bitrate;
- horizon;
- segment duration;
- internal QoE/smoothness weights;
- target buffer/stability parameters.

But these are not mapped fully in Phase 2.2A because SODA is not initial.

## Decision

```text
Decision: document only.
Implementation status: deferred.
Reason: strong modern candidate, but more complex than mandatory baselines.
```

## What SODA does not justify now

- It does not justify changing the mandatory implementation order.
- It does not justify skipping BBA/BOLA/MPC/RobustMPC.
- It does not justify defining final QoE/reward now.
- It does not justify low-latency live benchmark now.
- It does not justify implementing production Amazon behavior.

## Use in memory

Chapter 2:
- cite as recent non-neural ABR work focused on smoothness and robustness.

Chapter 5:
- mention as deferred optional candidate, not implemented in the first system.

Chapter 6:
- possibly mention as future work if not implemented.

Suggested table:
- "Modern optional candidates" with SODA as selected candidate and RBC as backup.

Suggested defense message:
- "The project implements established mandatory classical baselines first; SODA was identified as a recent strong non-neural extension candidate but deferred to avoid scope creep."