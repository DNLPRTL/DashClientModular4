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

## Phase 3.2A Source-Triage Update

### Chapter 6 Material Now Available

- Dataset selection rationale table.
- Replay/emulation method comparison table.
- Threats to validity: exogenous trace assumption, log-derived trace bias, split leakage, storage/format risks.
- OOD/generalization policy.
- Explanation that smoke/fake tests are not benchmark evidence.

### Planned Figures

- Evaluation pipeline: source PDFs/source pages -> cards -> matrix -> trace schema -> runner -> Phase 3.5 metrics -> Phase 6 comparison.
- Replay method decision tree: Python runner first, Mahimahi secondary, netem fallback.
- Dataset domain ladder: synthetic, HSDPA, LTE, HAS, 4G KPI, 5G KPI, mmWave 5G, FCC/Puffer references.

### Planned Tables

- Source triage table.
- Dataset matrix table.
- Method comparison table.
- Leakage risks by dataset.
- Candidate split policy table.

### Defense Talking Points

- Phase 3.2A intentionally does not implement code because dataset/replay choices must be defensible first.
- The first implementation will prioritize determinism and testability.
- Mahimahi and netem are considered but not forced prematurely.
- Puffer and CausalSim/Veritas prevent overclaiming trace-driven results.

## Phase 3.2B Schema Update

Chapter 6 can now describe the trace input contract:

- `normalized_trace_schema_v1` uses `timestamp_s`, `duration_s` and `throughput_kbps`;
- canonical throughput is `kbps`;
- trace provenance uses `trace_manifest_v1`;
- split provenance uses `split_manifest_v1`;
- raw and normalized real traces stay outside the repository;
- QoE/reward remains deferred to Phase 3.5;
- IA/RL remains deferred, but the schema and split policies protect future IA work from leakage.

Suggested defense sentence: Phase 3.2B prepares reproducible network inputs without implementing replay or claiming performance.
