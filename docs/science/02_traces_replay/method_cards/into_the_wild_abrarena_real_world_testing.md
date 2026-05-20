# Method card — Into the Wild / ABR-Arena

## Identity

- Method/source: Benjamin Hoffman, Alexander Dietmüller, Ayush Mishra, Laurent Vanbever. *Into the Wild: Real-World Testing for ML-Based ABR*. PACMI 2025.
- Type: real-world generalization/testing methodology for ML-based ABR.
- Phase 3.2A status: recommended optional method card.
- Phase 3.2A decision: future generalization reference; not an implementation target.

## Problem solved

The paper argues that ML-based ABR algorithms can fail to generalize from simulation or a single real-world environment to diverse global network contexts. It proposes ABR-Arena as a global testing platform.

## What it emulates or replays

Not a local replay runner. It is a real-world testing infrastructure concept.

## Inputs

- ABR algorithms.
- Real-world streaming servers/clients across regions.
- User/testing environments.

## Outputs

- Performance observations across diverse real-world settings.

## Platform requirements

Out of scope for Phase 3.

## Windows support

Not applicable.

## Ubuntu support

Not applicable.

## Reproducibility and determinism

Useful for explaining generalization limits, not for local deterministic tests.

## Required privileges

Not applicable.

## Integration risks

- Too large for current TFG phase.
- Focuses on ML-based ABR, which belongs to later phases.

## Test strategy

No implementation or tests in Phase 3.2A.

## Why useful for DashClientModular4

It strengthens the rationale for OOD evaluation and careful claims when the future IA controller is evaluated.

## Why not enough alone

It does not provide a local dataset or replay mechanism for the current Phase 3 implementation path.

## Decision

`recommended-future-generalization-reference`

## Memory usage

- Chapter 6: OOD/generalization motivation.
- Future work / limitations.

## BibTeX provisional

```bibtex
@inproceedings{hoffman2025intoTheWildABR,
  title = {Into the Wild: Real-World Testing for ML-Based ABR},
  author = {Hoffman, Benjamin and Dietmuller, Alexander and Mishra, Ayush and Vanbever, Laurent},
  booktitle = {Practical Adoption Challenges of ML for Systems},
  year = {2025}
}
```
