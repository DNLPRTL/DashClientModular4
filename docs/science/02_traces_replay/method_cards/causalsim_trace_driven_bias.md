# Method card — CausalSim and trace-driven simulation bias

## Identity

- Method/source: CausalSim.
- Primary source: Abdullah Alomar, Pouya Hamadanian, Arash Nasr-Esfahany, Anish Agarwal, Mohammad Alizadeh, Devavrat Shah. *CausalSim: A Causal Framework for Unbiased Trace-Driven Simulation*. USENIX NSDI 2023.
- Type: causal framework and validity-threat reference for trace-driven simulation.
- Phase 3.2A status: mandatory method card.
- Phase 3.2A decision: mandatory threats-to-validity reference; not an implementation target.

## Problem solved

CausalSim addresses a core weakness of naive trace-driven simulation: the assumption that an intervention, such as changing the ABR algorithm, would not affect the trace being replayed. In ABR, measured throughput can depend on the bitrate decisions made during collection, so replaying achieved-throughput traces under a different controller may be biased.

## What it emulates or replays

CausalSim does not simply replay traces. It models latent system factors and the causal effect of actions on observed traces, using RCT data to reduce bias.

## Inputs

- Traces from randomized control trials under a fixed set of algorithms.
- Observed actions/decisions.
- Observed system states and outcomes.

## Outputs

- Bias-corrected simulation predictions for new interventions.
- A causal interpretation of trace-driven results.

## Platform requirements

Not an implementation target for this TFG phase.

## Windows support

Not applicable.

## Ubuntu support

Not applicable.

## Reproducibility and determinism

Useful as a methodological constraint rather than as a runner. It forces Phase 3 documentation to distinguish exogenous capacity traces from achieved-throughput logs influenced by previous ABR actions.

## Required privileges

Not applicable.

## Integration risks

- Full causal framework is out of scope.
- Overusing it could derail Phase 3 into a research problem beyond the TFG scope.
- Ignoring it would make final claims too strong.

## Test strategy

- No implementation in Phase 3.2A.
- Add caveats to leakage prevention, generalization protocol and dataset selection.
- For log-derived datasets, mark causal/trace-bias risk explicitly.

## Why useful for DashClientModular4

It makes the evaluation methodology academically defensible and prevents naive claims that all throughput traces represent invariant network capacity.

## Why not enough alone

It requires RCT-style data/modeling that the TFG does not currently have and is not needed for the first controlled runner.

## Decision

`mandatory-validity-threat-reference-no-implementation`

## Memory usage

- Chapter 6: threats to validity.
- Defense: explain the exogenous trace assumption and why benchmark claims will be scoped.

## BibTeX provisional

```bibtex
@inproceedings{alomar2023causalsim,
  title = {CausalSim: A Causal Framework for Unbiased Trace-Driven Simulation},
  author = {Alomar, Abdullah and Hamadanian, Pouya and Nasr-Esfahany, Arash and Agarwal, Anish and Alizadeh, Mohammad and Shah, Devavrat},
  booktitle = {20th USENIX Symposium on Networked Systems Design and Implementation},
  year = {2023}
}
```
