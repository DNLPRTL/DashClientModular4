# Method card — Wei et al. trace-based emulation for ABR throughput prediction

## Identity

- Method/source: Bo Wei et al. *Evaluation of Throughput Prediction for Adaptive Bitrate Control Using Trace-Based Emulation*. IEEE Access 2019.
- Type: trace-based DASH emulation methodology and throughput-prediction evaluation.
- Phase 3.2A status: recommended optional method card.
- Phase 3.2A decision: optional methodology support; not an implementation target.

## Problem solved

The paper builds a reproducible trace-based emulation environment to compare throughput prediction methods under artificially identical network conditions. It is relevant to the Phase 3 design goal of controlled evaluation, but the specific throughput-prediction algorithms are not part of this phase.

## What it emulates or replays

- A DASH client/server setup on localhost.
- Throughput constrained according to input traces by controlling/delaying HTTP responses.

## Inputs

- Throughput traces.
- DASH video content and MPD.
- Throughput prediction algorithms.

## Outputs

- QoE-related outcomes under controlled trace-based conditions.

## Platform requirements

Original stack is not a required dependency for DashClientModular4.

## Windows support

Not a direct path.

## Ubuntu support

Not a direct path.

## Reproducibility and determinism

Methodologically useful because it motivates identical-condition experiments. Exact implementation should not be imported without specification.

## Required privileges

TBD. The localhost server approach can avoid some privileged network manipulation, which is conceptually relevant to a custom Python runner.

## Integration risks

- Could blur the line between throughput prediction and ABR controller evaluation.
- Could introduce non-project-specific server code.
- QoE metric in the paper must not be imported before Phase 3.5.

## Test strategy

- No implementation in Phase 3.2A.
- Use as a supporting reference for replay runner requirements.

## Why useful for DashClientModular4

It supports the decision that a controlled trace-driven runner can be a legitimate first implementation path when documented and tested carefully.

## Why not enough alone

It is not a ready-made DashClientModular4 integration and does not solve dataset selection or split policy.

## Decision

`recommended-optional-methodology-support`

## Memory usage

- Chapter 6: controlled emulation methodology.
- Defense: explain reproducible identical-condition testing.

## BibTeX provisional

```bibtex
@article{wei2019traceBasedEmulation,
  title = {Evaluation of Throughput Prediction for Adaptive Bitrate Control Using Trace-Based Emulation},
  author = {Wei, Bo and Song, Hang and Wang, Shangguang and Kanai, Kenji and Katto, Jiro},
  journal = {IEEE Access},
  year = {2019}
}
```
