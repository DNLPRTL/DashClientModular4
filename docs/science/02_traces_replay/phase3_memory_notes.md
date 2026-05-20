# Phase 3 Memory Notes

These notes map Phase 3 trace/replay methodology into the final TFG memory. They are planning material, not final thesis prose.

## Chapter 6 Usage

Use Phase 3 to explain why controller implementation is not enough for scientific evaluation. The memory should separate:

- implemented controller validity from Phase 2;
- reproducible network methodology from Phase 3;
- final QoE/reward and benchmark ranking from later phases.

## Defense Usage

Good defense statements:

- Phase 2 produced a stable baseline controller set.
- Phase 3 defines how those controllers will be exposed to reproducible network conditions.
- Dataset selection is documented before downloads or benchmarks.
- Mahimahi is considered as a methodological reference, while simpler deterministic runners may be more appropriate for local Python tests.
- OOD traces are planned separately from in-domain test traces to avoid overclaiming.

Avoid saying:

- a dataset has been selected before `trace_dataset_selection.md` is complete;
- Puffer or FCC raw data has been integrated;
- Mahimahi is already implemented;
- any controller is better than another;
- any QoE/reward is final.

## Candidate Figures And Tables

- Trace/dataset selection pipeline.
- Replay/emulation decision matrix.
- Dataset candidate matrix.
- Train/validation/test/OOD split diagram.
- Leakage prevention checklist.
- Artifact lifecycle diagram.

## Memory Boundary

Phase 3.1 is a methodology scaffold. It should be cited in the thesis as planning and traceability evidence, not as experimental results.

