# Trace Schema Risks And Open Decisions

This document records risks that remain after defining `normalized_trace_schema_v1`.

## Risks

| risk | impact | mitigation |
| --- | --- | --- |
| Source unit ambiguity | Wrong throughput conversion can invalidate all later results. | Require dataset-specific converter notes and manifest fields. |
| Inferred duration ambiguity | Last-row or irregular sampling duration may be unclear. | Document per-dataset duration policy before conversion. |
| Achieved-throughput bias | Logs may reflect decisions made by a deployed ABR algorithm. | Treat Puffer and similar logs as causal-risk sources until a causal plan exists. |
| Future-sample leakage | A runner could accidentally let controllers see future throughput. | Acceptance tests must check controller signal boundaries. |
| Context leakage | KPI/location/app metadata could leak into baseline controller decisions. | Preserve optional context only as metadata unless later approved for IA. |
| Split leakage | Windows from the same route/session/day could cross splits. | Use `leakage_group` in trace and split manifests. |
| Storage creep | Real traces or generated manifests could enter git. | Keep raw, normalized and generated manifest files outside the repository. |
| Benchmark overclaiming | Schema validation could be mistaken for performance evidence. | Keep QoE/reward and ranking deferred to Phase 3.5 and later. |

## Open Decisions

- Exact raw-download block scope for HSDPA Norway, Ghent 4G and Lancaster.
- Exact converter implementation paths and tests.
- Final synthetic fixture storage policy.
- Dataset-specific rules for irregular sampling and final-row duration.
- Whether Lancaster traces should be grouped by service/day, trace source or another metadata field.
- Whether Raca 4G/5G context fields should be retained verbatim or reduced to safe labels.
- Whether Lumos5G trajectory metadata is sufficient for OOD grouping.
- Whether any external Mahimahi or `tc/netem` validation is needed after the Python runner exists.
- Final QoE/reward, explicitly deferred to Phase 3.5.
- Final IA/RL method choices, explicitly deferred.

## Closure Requirement

These risks must be revisited before:

- converter implementation;
- replay runner implementation;
- dataset download;
- train/validation/test/OOD split freeze;
- final QoE/reward definition;
- benchmark ranking.

