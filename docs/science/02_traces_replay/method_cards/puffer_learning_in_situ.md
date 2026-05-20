# Method card — Puffer/Fugu learning in situ

## Identity

- Method/source: Puffer/Fugu real-world randomized video-streaming experiment.
- Primary source: Francis Y. Yan et al. *Learning in situ: a randomized experiment in video streaming*. USENIX NSDI 2020.
- Type: real-world deployment methodology and warning against overtrusting simulators/emulators.
- Phase 3.2A status: mandatory method card.
- Phase 3.2A decision: mandatory methodology reference; not a dataset download target now.

## Problem solved

Puffer evaluates ABR algorithms in a public video-streaming service with randomized assignment. It demonstrates that results from emulation/simulation may differ from real-world performance and that learned/sophisticated methods may fail to beat simpler schemes in deployment.

## What it emulates or replays

Puffer itself is not just an emulator. The paper includes comparisons with emulation and reports real-world randomized trial results.

## Inputs

- Real user video sessions.
- ABR algorithm assignments.
- Chunk-level telemetry.
- TCP/network statistics depending on experiment.

## Outputs

- Real-world streaming metrics, including stall behavior and perceptual quality metrics.
- Statistical uncertainty and confidence intervals.
- Public data/results archive.

## Platform requirements

No implementation target in Phase 3.2A.

## Windows support

Not applicable.

## Ubuntu support

Not applicable for this block.

## Reproducibility and determinism

The paper is valuable precisely because it highlights that deterministic offline replay does not fully capture the real Internet. Puffer raw data can support later analysis, but only after a storage/conversion/causal plan.

## Required privileges

Not applicable.

## Integration risks

- Puffer raw data is large and complex.
- Logs are influenced by deployed ABR decisions, so they are not simple exogenous throughput traces.
- Using Puffer too early risks scope creep into causal modeling or real-world deployment.

## Test strategy

- Do not download Puffer raw data in Phase 3.2A.
- Use the paper to shape threats-to-validity, generalization and defense notes.
- Keep Puffer as metadata-only until Phase 3 has a conversion/storage plan.

## Why useful for DashClientModular4

It prevents false confidence from fake/synthetic tests and provides a defensible explanation for why final claims must be scoped carefully.

## Why not enough alone

It does not provide a small first integration dataset and does not solve local replay implementation.

## Decision

`mandatory-real-world-methodology-reference-metadata-only-data`

## Memory usage

- Chapter 6: threats to validity and real-world limitations.
- Defense: explain why reproducible local replay is necessary but not equivalent to deployment.

## BibTeX provisional

```bibtex
@inproceedings{yan2020puffer,
  title = {Learning in situ: a randomized experiment in video streaming},
  author = {Yan, Francis Y. and Ayers, Hudson and Zhu, Chenzhi and Fouladi, Sadjad and Hong, James and Zhang, Keyi and Levis, Philip and Winstein, Keith},
  booktitle = {17th USENIX Symposium on Networked Systems Design and Implementation},
  year = {2020}
}
```
