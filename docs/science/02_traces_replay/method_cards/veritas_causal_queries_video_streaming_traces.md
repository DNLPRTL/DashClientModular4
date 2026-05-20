# Method card — Veritas causal queries from video streaming traces

## Identity

- Method/source: Veritas.
- Primary source: Chandan Bothra, Jianfei Gao, Sanjay Rao, Bruno Ribeiro. *Veritas: Answering Causal Queries from Video Streaming Traces*. ACM SIGCOMM 2023.
- Type: causal reasoning framework for video streaming traces.
- Phase 3.2A status: recommended optional method card.
- Phase 3.2A decision: optional threats-to-validity/future-work reference; not an implementation target.

## Problem solved

Veritas addresses what-if questions in video streaming from passively collected traces, such as changing the ABR algorithm, buffer size or available qualities, without requiring randomized control trial data.

## What it emulates or replays

It does not provide a simple replay runner. It performs causal reasoning over recorded video sessions by modeling latent bandwidth and observed download behavior.

## Inputs

- Recorded video streaming sessions.
- Chunk sizes and download times.
- TCP-state/control information depending on experiment.
- Proposed counterfactual change.

## Outputs

- Predicted outcomes for what-if/counterfactual queries.

## Platform requirements

Not a Phase 3 implementation target.

## Windows support

Not applicable.

## Ubuntu support

Not applicable.

## Reproducibility and determinism

Useful as a methodological caveat and future-work pointer; too complex for first replay infrastructure.

## Required privileges

Not applicable.

## Integration risks

- Scope creep into causal ML.
- Could distract from building the required simple reproducible replay path.
- Not needed to compare Phase 2 baselines under controlled synthetic/trace conditions.

## Test strategy

No tests in Phase 3.2A.

## Why useful for DashClientModular4

It reinforces the CausalSim caveat that observed video-streaming traces are not automatically valid for arbitrary counterfactual ABR comparisons.

## Why not enough alone

It is not a dataset, not an emulator and not the replay runner needed in Phase 3.

## Decision

`recommended-optional-causal-methodology-reference`

## Memory usage

- Chapter 6: threats to validity.
- Future work: causal evaluation of log-derived traces.

## BibTeX provisional

```bibtex
@inproceedings{bothra2023veritas,
  title = {Veritas: Answering Causal Queries from Video Streaming Traces},
  author = {Bothra, Chandan and Gao, Jianfei and Rao, Sanjay and Ribeiro, Bruno},
  booktitle = {Proceedings of ACM SIGCOMM},
  year = {2023}
}
```
