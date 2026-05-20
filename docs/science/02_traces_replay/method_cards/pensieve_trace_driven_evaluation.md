# Method card — Pensieve trace-driven evaluation methodology

## Identity

- Method/source: Pensieve evaluation methodology.
- Primary source: Hongzi Mao, Ravi Netravali, Mohammad Alizadeh. *Neural Adaptive Video Streaming with Pensieve*. ACM SIGCOMM 2017.
- Type: ABR paper with trace-driven simulation/emulation methodology and RL controller.
- Phase 3.2A status: mandatory method card.
- Phase 3.2A decision: use methodology context only; do not implement IA/RL here.

## Problem solved

Pensieve shows a trace-driven evaluation structure for ABR controllers across broadband and HSDPA conditions and compares classic ABR algorithms such as buffer-based, rate-based, BOLA, MPC and robustMPC.

## What it emulates or replays

- Chunk-level simulation for training.
- Network traces reformatted for Mahimahi in evaluation.
- Broadband and HSDPA trace corpora.

## Inputs

- Throughput traces.
- Video chunk sizes and available bitrates.
- Buffer state and recent throughput observations.
- QoE reward definition in the paper.

## Outputs

- ABR decisions and QoE comparison over trace corpora.
- Training/test evaluation results.

## Platform requirements

The original implementation stack is old and should not drive Phase 3 implementation. Use this source for methodology and historical comparison only.

## Windows support

No direct implementation target.

## Ubuntu support

No direct implementation target in Phase 3.

## Reproducibility and determinism

The paper provides useful trace split and evaluation design ideas, but DashClientModular4 must not inherit its reward or IA training setup automatically.

## Required privileges

Not applicable for Phase 3.2A.

## Integration risks

- Scope creep into IA/RL before Phase 4.
- Importing Pensieve reward/QoE before Phase 3.5.
- Assuming Pensieve’s trace preprocessing is automatically valid for the current client.
- Reusing similar trace sources without documenting train/test/OOD separation.

## Test strategy

- Do not test or implement Pensieve in this block.
- Use its methodology to inform dataset cards and split-policy documents.
- Use CausalSim/Veritas caveats to avoid overclaiming trace-driven validity.

## Why useful for DashClientModular4

It anchors Fase 3 in a well-known ABR evaluation lineage and directly references controller families already implemented in Phase 2: rate-based, BBA/BOLA, MPC and robustMPC.

## Why not enough alone

It is an IA/RL system and includes reward/training decisions that belong to later phases. Its simulator/emulator assumptions must be treated as historical reference, not as automatic authority.

## Decision

`mandatory-methodology-reference-no-implementation`

## Memory usage

- Chapter 2: state of the art.
- Chapter 6: trace-driven methodology background.
- Defense: explain why Pensieve is cited but not implemented in Phase 3.

## BibTeX provisional

```bibtex
@inproceedings{mao2017pensieve,
  title = {Neural Adaptive Video Streaming with Pensieve},
  author = {Mao, Hongzi and Netravali, Ravi and Alizadeh, Mohammad},
  booktitle = {Proceedings of ACM SIGCOMM},
  year = {2017}
}
```
