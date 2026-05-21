# Phase 3.2B Closure Report

Phase 3.2B defines the common trace schema and dataset conversion plan for Phase 3.

## Closed In This Block

- `normalized_trace_schema_v1` is a CSV-like time series.
- Required columns are `timestamp_s`, `duration_s` and `throughput_kbps`.
- Canonical throughput unit is `kbps`.
- Time unit is seconds.
- RTT and jitter unit is milliseconds.
- `trace_manifest_v1` is defined as JSON/JSONL-compatible metadata.
- `split_manifest_v1` is defined as JSON-compatible split metadata.
- Raw, normalized and manifest storage paths are outside the repository.
- First real integration candidates are HSDPA Norway, Ghent 4G/LTE and Lancaster.
- Modern/OOD candidates are Raca 4G, Raca 5G and Lumos5G.
- FCC remains reference-only.
- Puffer archive remains metadata-only.
- Custom Python trace-driven fake/replay runner remains the likely primary implementation path, but is not implemented.
- Mahimahi remains a secondary Ubuntu validation candidate.
- Linux `tc/netem` remains a Linux fallback/runbook candidate.

## Not Closed

- no dataset download;
- no converter implementation;
- no replay implementation;
- no final QoE/reward;
- no benchmark ranking;
- no final train/validation/test/OOD split;
- no IA/RL method selection;
- no controller/player/runtime/media-engine/metric changes.

## Implementation Readiness Gate

Replay implementation is not authorized until these documents are accepted as the active input contract:

- `common_trace_schema.md`
- `trace_manifest_schema.md`
- `trace_conversion_plan.md`
- `trace_split_manifest_policy.md`
- `trace_schema_acceptance_tests.md`

## Next Logical Phase

A later block may design or implement converter validation and tiny synthetic fixtures. Any such block must explicitly authorize code paths, tests and fixture storage. Real dataset downloads must remain outside the repository and require a separate download/conversion block.

