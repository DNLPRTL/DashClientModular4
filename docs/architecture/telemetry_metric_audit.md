# Telemetry Metric Audit

Date: 2026-05-11

This audit classifies current CSV telemetry for Phase 1 hardening. It covers `segment_telemetry.csv` and the compact `evaluation_segments.csv` output. It does not define final QoE, final reward, academic baselines, final IA training data, or final benchmark methodology.

For full column-by-column provenance, including source module/function, unit, timing/source event, semantic status, benchmark usability, and risks, see `docs/architecture/telemetry_column_provenance.md`. This file remains the shorter metric-risk summary from the neutrality block.

Block 14 adds `docs/architecture/metric_catalog.md` for producer/consumer/formula decisions and exposes the current default feedback keys in code so validation does not invent telemetry columns.

Classification labels:

- `eval_ready`: allowed as evaluation-oriented context when `use_for_eval=true`; not a final score by itself.
- `runtime_only`: useful for reproducing or debugging runtime behavior, not a benchmark metric.
- `legacy_debug`: retained for compatibility/debugging; do not use for benchmark scoring.
- `pending_semantics`: recorded, but final benchmark interpretation is not defined yet.
- `deprecated_later`: keep for now, consider removal or replacement after Phase 1 acceptance.

Rows where `use_for_eval=false` are not benchmark rows. Terminal drain stalls must not be counted as steady-state rebuffering.

Console/progress output is not a telemetry artifact and must not be parsed by benchmark scripts. See `docs/architecture/runtime_console_output_contract.md`.

| Name | Source | Units | Class | Final Benchmark Score Now | Risk / Notes |
|---|---|---:|---|---|---|
| `segment_index` | Player row assembly | index | runtime_only | No | Top-level row identity; feedback has separate prefixed copy. |
| `timestamp` | `time.time()` | unix_seconds | runtime_only | No | Wall-clock logging only; not stable enough for scoring. |
| `feedback_queued_bytes` | media engine feedback | bytes | pending_semantics | No | Buffer byte semantics differ by engine and media representation. |
| `feedback_queued_time` | media engine feedback | seconds | pending_semantics | No | Useful for future buffer metrics, but fake/GStreamer equivalence is not claimed. |
| `feedback_cur_bitrate` | Player current ladder rate | bytes_per_second | eval_ready | No | Evaluation context only; use only on `steady_state` rows with `use_for_eval=true`. |
| `feedback_bwe` | Player/runtime feedback | bytes_per_second | legacy_debug | No | Current estimator is last-download-size over last-download-time with current-rate fallback; final throughput methodology pending. |
| `feedback_level` | Player current level | quality_level_index | eval_ready | No | Selected representation context on evaluable rows; final scoring is pending. |
| `feedback_max_level` | Player ladder metadata | quality_level_index | runtime_only | No | Run context / controller guardrail. |
| `feedback_cur_rate` | Player current ladder rate | bytes_per_second | eval_ready | No | Duplicates `feedback_cur_bitrate`; keep for compatibility. Prefer "representation rate" in human docs/UI. |
| `feedback_max_rate` | Player ladder metadata | bytes_per_second | runtime_only | No | Ladder context, not a score. |
| `feedback_min_rate` | Player ladder metadata | bytes_per_second | runtime_only | No | Ladder context, not a score. |
| `feedback_max_bitrate` | Player ladder metadata | bytes_per_second | runtime_only | No | Legacy duplicate of max rate. |
| `feedback_min_bitrate` | Player ladder metadata | bytes_per_second | runtime_only | No | Legacy duplicate of min rate. |
| `feedback_last_fragment_size` | downloader/player row context | bytes | pending_semantics | No | Input for future throughput metrics; semantics depend on retries and init/media filtering. |
| `feedback_last_download_time` | downloader/player row context | seconds | pending_semantics | No | Input for future throughput metrics; final treatment of retries pending. |
| `feedback_downloaded_bytes` | Player cumulative counter | bytes | runtime_only | No | Runtime progress counter. |
| `feedback_fragment_duration` | parser/player row context | seconds | eval_ready | No | Segment duration context on evaluable rows; not a score. |
| `feedback_rates` | controller feedback ladder | bytes_per_second_list | runtime_only | No | Serialized Python list in CSV; debug/context only. |
| `feedback_segment_index` | controller feedback index | index | runtime_only | No | Contract trace; top-level `segment_index` is canonical row identity. |
| `feedback_start_segment_request` | Player timing | perf_counter_seconds | runtime_only | No | Local runtime trace, not benchmark score. |
| `feedback_stop_segment_request` | Player timing | perf_counter_seconds | runtime_only | No | Local runtime trace, not benchmark score. |
| `is_init` | Player row assembly | boolean_int | eval_ready | No | Eligibility context only. Init rows must be excluded from benchmark rows. |
| `retry_count` | Player retry loop | count | pending_semantics | No | Retry behavior is unchanged; benchmark treatment pending. |
| `segment_start_time` | Player timing | perf_counter_seconds | runtime_only | No | Local runtime trace. |
| `segment_end_time` | Player timing | perf_counter_seconds | runtime_only | No | Local runtime trace. |
| `wall_time_elapsed` | Player timing | seconds | pending_semantics | No | Useful for phase tagging; final scoring semantics pending. |
| `tp_now` | derived features | bytes_per_second | pending_semantics | No | Current throughput feature, not final methodology. |
| `tp_ewma` | derived features | bytes_per_second | pending_semantics | No | Current smoothing is not final benchmark methodology. |
| `tp_min_last5` | derived features | bytes_per_second | pending_semantics | No | Window semantics are not final. |
| `tp_std_last5` | derived features | bytes_per_second | pending_semantics | No | Window semantics are not final. |
| `buffer_over_seg` | derived features | ratio | pending_semantics | No | Candidate feature, not final QoE. |
| `headroom` | derived features | ratio | pending_semantics | No | Candidate feature, not final QoE. |
| `is_upswitch` | policy/switch annotation | boolean_int | pending_semantics | No | Useful for future switch metrics; scoring not final. |
| `is_downswitch` | policy/switch annotation | boolean_int | pending_semantics | No | Useful for future switch metrics; scoring not final. |
| `switch_magnitude` | policy/switch annotation | levels | pending_semantics | No | Future switch penalty semantics pending. |
| `phase_raw` | Player phase detector | label | legacy_debug | No | Runtime/debug phase, separate from benchmark `eval_phase`. |
| `phase_smooth` | Player phase detector | label | legacy_debug | No | Runtime/debug phase, separate from benchmark `eval_phase`. |
| `policy_name` | controller metadata | label | runtime_only | No | Identifies policy/controller for run trace only. |
| `policy_target_rate` | controller output | bytes_per_second | pending_semantics | No | Useful for controller trace; final scoring uses selected/evaluable rows. |
| `policy_chosen_level` | Player quantization result | quality_level_index | pending_semantics | No | Useful for quantization trace; final switch metrics pending. |
| `policy_decision_ms` | controller timing | milliseconds | runtime_only | No | Local timing can be noisy; not benchmark-grade. |
| `eval_phase` | `core.benchmark_contract` | label | eval_ready | No | Canonical phase for benchmark eligibility; not a score. |
| `is_preroll` | Player preroll marker | boolean_int | pending_semantics | No | Legacy/startup marker; use `eval_phase` and `use_for_eval` for eligibility. |
| `use_for_eval` | `core.benchmark_contract` | boolean_int | eval_ready | No | Canonical row-level benchmark eligibility flag; not a score. |
| `stall_flag` | media-engine event aggregate | boolean_int | pending_semantics | No | Segment-level aggregate only; event-level stall class is pending. |
| `stall_duration` | media-engine event aggregate | seconds | pending_semantics | No | Do not count terminal drain stalls as steady-state rebuffering. |

`evaluation_segments.csv` carries a smaller subset: `segment_index`, `is_init`, `eval_phase`, `use_for_eval`, `last_fragment_size`, `last_download_time`, and `fragment_duration`. Its rows follow the same evaluation eligibility rule: `use_for_eval=false` means the row is not a benchmark row. It is an evaluation-oriented control artifact, not a final IA training dataset.
