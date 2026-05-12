# Telemetry Column Provenance

Date: 2026-05-11

This document records source, unit, timing, semantic status, and benchmark usability for the current CSV columns written by `segment_telemetry.csv` and `evaluation_segments.csv`.

It documents the current implementation; it does not define final QoE, reward, AI training data, or benchmark methodology. When a field is useful later, it is still gated by future methodology unless the table says it is only a row gate.

## Status Labels

- `runtime-only`: useful to reproduce or debug a run, not a benchmark metric.
- `eval-gated`: meaningful only through `eval_phase` and `use_for_eval`.
- `benchmark-neutral`: metadata that separates phases or eligibility without scoring.
- `pending methodology`: recorded value exists, but final academic interpretation is undecided.
- `debug/test-only`: diagnostic or deterministic-test context.
- `deprecated/legacy alias`: kept for compatibility or historical naming; prefer clearer terminology in future APIs.

## Schema Notes

`segment_telemetry.csv` is built by `core.dataset_schema.build_segment_telemetry_header()` using the feedback key order returned by `core.runtime_feedback.build_controller_feedback()`. Feedback-derived columns are prefixed with `feedback_`.

Block 14 makes that key order explicit through `core.controller.contract.CURRENT_FEEDBACK_KEYS`, `core.dataset_schema.DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS`, and `core.dataset_schema.build_default_segment_telemetry_header()`. Readiness checks must use those real keys, not invented examples.

The default feedback keys are: `queued_bytes`, `queued_time`, `cur_bitrate`, `bwe`, `level`, `max_level`, `cur_rate`, `max_rate`, `min_rate`, `max_bitrate`, `min_bitrate`, `last_fragment_size`, `last_download_time`, `downloaded_bytes`, `fragment_duration`, `rates`, `segment_index`, `start_segment_request`, and `stop_segment_request`.

Controllers may add feedback keys through `augment_feedback()`. Such extra columns are outside this current-column audit and must receive their own provenance before benchmark use.

## `segment_telemetry.csv`

| Column | Artifact | Source module/function | Unit | Timing/source event | Semantic status | Direct benchmark use now? | Notes/risks |
|---|---|---|---|---|---|---|---|
| `segment_index` | `segment_telemetry.csv` | `player.Player.run` row assembly | index | Captured when the row is assembled for the current segment. | runtime-only | No | Canonical row identity; distinct from `feedback_segment_index`. |
| `timestamp` | `segment_telemetry.csv` | `player.Player.run`, `time.time()` | unix seconds | Captured when CSV row values are assembled. | runtime-only | No | Wall-clock trace only; not stable scoring input. |
| `feedback_queued_bytes` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `media_engine.get_queued_bytes()` | bytes | Controller feedback snapshot after init/download handling. | pending methodology | No | Buffer bytes are engine-dependent and not comparable across fake/GStreamer yet. |
| `feedback_queued_time` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `media_engine.get_queued_time()` | seconds | Controller feedback snapshot after init/download handling. | pending methodology | No | Candidate buffer signal; fake and GStreamer timing equivalence is not claimed. |
| `feedback_cur_bitrate` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `rates[cur_level]` | bytes per second | Controller feedback snapshot for current selected level. | eval-gated; deprecated/legacy alias | Not as final score | Name says bitrate but value is bytes/s representation rate. Prefer "representation rate" in docs/UI. |
| `feedback_bwe` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback` | bytes per second | Controller feedback snapshot after last download; `last_size / last_time` when available, otherwise current representation rate. | deprecated/legacy alias; pending methodology | No | Legacy controller key. It is a measured download-rate fallback signal, not a final bandwidth-estimation method. |
| `feedback_level` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.cur_level` | quality level index | Controller feedback snapshot for current selected level. | eval-gated | Not as final score | Candidate selected-level context after future methodology. |
| `feedback_max_level` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback` | quality level index | Controller feedback snapshot. | runtime-only | No | Ladder guardrail/context. |
| `feedback_cur_rate` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `rates[cur_level]` | bytes per second | Controller feedback snapshot for current selected level. | eval-gated; deprecated/legacy alias | Not as final score | Duplicate of `feedback_cur_bitrate` with clearer unit semantics but still legacy contract. |
| `feedback_max_rate` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `max(rates)` | bytes per second | Controller feedback snapshot. | runtime-only | No | Ladder context only. |
| `feedback_min_rate` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `min(rates)` | bytes per second | Controller feedback snapshot. | runtime-only | No | Ladder context only. |
| `feedback_max_bitrate` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `max(rates)` | bytes per second | Controller feedback snapshot. | deprecated/legacy alias | No | Duplicate of `feedback_max_rate`; name is ambiguous because value is bytes/s. |
| `feedback_min_bitrate` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `min(rates)` | bytes per second | Controller feedback snapshot. | deprecated/legacy alias | No | Duplicate of `feedback_min_rate`; name is ambiguous because value is bytes/s. |
| `feedback_last_fragment_size` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.get_feedback()` arguments | bytes | Last init/media download context; media rows use downloaded segment size, init rows use 0. | pending methodology | No | Throughput input; retry and init/media handling need methodology before scoring. |
| `feedback_last_download_time` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; downloader `elapsed_total` fallback to request wall time | seconds | Last init/media download context; media rows use measured download time, init rows use 0 or init time depending path. | pending methodology | No | Throughput input; treatment of retries and downloader timing remains methodology work. |
| `feedback_downloaded_bytes` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.downloaded_bytes` | bytes | Cumulative successful media bytes at feedback snapshot. | runtime-only | No | Excludes virtual init and increments only after successful media downloads in current code. |
| `feedback_fragment_duration` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; parser/player duration context | seconds | Feedback snapshot for current fragment; init rows pass 0. | eval-gated | Not as final score | Segment-duration context, not QoE by itself. |
| `feedback_rates` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.rates` | list of bytes per second | Feedback snapshot. | runtime-only | No | Python list serialized by CSV; use manifest/MPD inventory later for robust ladder provenance. |
| `feedback_segment_index` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.cur_index` | index | Feedback snapshot. | runtime-only | No | Controller-contract trace only; top-level `segment_index` is row identity. |
| `feedback_start_segment_request` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.start_segment_request` | `time.perf_counter()` seconds | Request start timestamp for current/last segment. | runtime-only | No | Local monotonic timestamp; not portable across runs. |
| `feedback_stop_segment_request` | `segment_telemetry.csv` | `core.runtime_feedback.build_controller_feedback`; `Player.stop_segment_request` | `time.perf_counter()` seconds | Request stop timestamp for current/last segment. | runtime-only | No | Local monotonic timestamp; not portable across runs. |
| `is_init` | `segment_telemetry.csv` | `player.Player.run` row assembly | boolean int | Segment row assembly. | benchmark-neutral; eval-gated | Gate/context only | Init rows are excluded by `use_for_eval`. |
| `retry_count` | `segment_telemetry.csv` | `player.Player.run` retry loop | count | Captured after successful download for the segment row. | pending methodology | No | Retry policy affects observations; benchmark interpretation is not final. |
| `segment_start_time` | `segment_telemetry.csv` | `player.Player.run`; `perf_now()` | `time.perf_counter()` seconds | Immediately before downloader call or virtual init handling. | runtime-only | No | Local timing trace. |
| `segment_end_time` | `segment_telemetry.csv` | `player.Player.run`; `perf_now()` | `time.perf_counter()` seconds | Immediately after downloader call or virtual init handling. | runtime-only | No | Local timing trace. |
| `wall_time_elapsed` | `segment_telemetry.csv` | `player.Player.run`; `perf_now() - start_time_global` | seconds | Captured after feedback update for the row. | pending methodology | No | Used for current phase/preroll tagging; not final startup/QoE definition. |
| `tp_now` | `segment_telemetry.csv` | `player.Player._compute_derived_features` | bytes per second | Derived after feedback snapshot; media rows compute `last_fragment_size / last_download_time`, init rows use 0. | pending methodology | No | Formula is known, but final throughput methodology is not defined. |
| `tp_ewma` | `segment_telemetry.csv` | `player.Player._compute_derived_features` | bytes per second | Updated when `tp_now > 0` using `TP_EWMA_ALPHA = 0.6`. | pending methodology | No | Smoothing exists for trace/debug; not a final estimator. |
| `tp_min_last5` | `segment_telemetry.csv` | `player.Player._compute_derived_features` | bytes per second | Minimum over current throughput history window `TP_WINDOW = 5`. | pending methodology | No | Window semantics are not final. |
| `tp_std_last5` | `segment_telemetry.csv` | `player.Player._compute_derived_features` | bytes per second | Sample standard deviation over current throughput history window `TP_WINDOW = 5`. | pending methodology | No | Window semantics are not final. |
| `buffer_over_seg` | `segment_telemetry.csv` | `player.Player._compute_derived_features` | ratio | Derived after feedback snapshot as `queued_time / fragment_duration` when duration is positive. | pending methodology | No | Candidate feature; not final QoE or safety margin. |
| `headroom` | `segment_telemetry.csv` | `player.Player._compute_derived_features` | ratio | Derived after feedback snapshot as `tp_now / cur_bitrate` when current rate is positive. | pending methodology | No | Candidate feature; current-rate naming is legacy bytes/s. |
| `is_upswitch` | `segment_telemetry.csv` | `player.Player._update_pending_policy_and_switch` | boolean int | Filled after controller decision for the current media segment; init/warm-up rows may remain 0. | pending methodology | No | Switch metric interpretation is pending. |
| `is_downswitch` | `segment_telemetry.csv` | `player.Player._update_pending_policy_and_switch` | boolean int | Filled after controller decision for the current media segment; init/warm-up rows may remain 0. | pending methodology | No | Switch metric interpretation is pending. |
| `switch_magnitude` | `segment_telemetry.csv` | `player.Player._update_pending_policy_and_switch` | quality levels | Filled after controller decision for the current media segment. | pending methodology | No | Future switch penalty semantics pending. |
| `phase_raw` | `segment_telemetry.csv` | `player.Player._PhaseDetector.update` | label | Derived after feedback snapshot from current buffer level and phase detector thresholds. | debug/test-only | No | Runtime/debug phase; separate from benchmark-neutral `eval_phase`. |
| `phase_smooth` | `segment_telemetry.csv` | `player.Player._PhaseDetector.update` | label | Smoothed phase after raw phase update. | debug/test-only | No | Runtime/debug phase; separate from benchmark-neutral `eval_phase`. |
| `policy_name` | `segment_telemetry.csv` | `player.Player.__init__`; controller `name` or class name | label | Stored at player construction, written in rows. | runtime-only | No | Run trace only; not a baseline identity until methodology names baselines. |
| `policy_target_rate` | `segment_telemetry.csv` | `player.Player.run`; controller `calcControlAction()` | bytes per second | Filled after controller decision for the current media segment. | pending methodology | No | Target-rate trace; final comparison should use documented controller methodology. |
| `policy_chosen_level` | `segment_telemetry.csv` | `player.Player.run`; controller `quantizeRate()` | quality level index | Filled after controller decision for the current media segment. | pending methodology | No | Quantized selection trace; switch/quality scoring pending. |
| `policy_decision_ms` | `segment_telemetry.csv` | `player.Player.run`; `perf_now()` around `calcControlAction()` | milliseconds | Filled after controller decision. | runtime-only | No | Local timing diagnostic; not benchmark-grade yet. |
| `eval_phase` | `segment_telemetry.csv` | `core.benchmark_contract.classify_segment_phase` via `player.Player._compute_derived_features` | label | Derived after feedback snapshot for each row. | benchmark-neutral; eval-gated | Gate only | Separates `init`, `startup`, `warmup`, `steady_state`, `drain`, `terminal`, and `error`. It is not a QoE score. |
| `is_preroll` | `segment_telemetry.csv` | `player.Player._compute_derived_features`; `wall_time_elapsed < PREROLL_SECONDS` | boolean int | Derived after feedback snapshot. | pending methodology | No | Current startup marker; use `eval_phase`/`use_for_eval` for row eligibility. |
| `use_for_eval` | `segment_telemetry.csv` | `core.benchmark_contract.should_use_segment_for_eval` via `player.Player._compute_derived_features` | boolean int | Derived after `eval_phase` for each row. | benchmark-neutral; eval-gated | Gate only | Canonical row-level eligibility flag; not a final benchmark score. |
| `stall_flag` | `segment_telemetry.csv` | `player.Player._on_media_event` and `_flush_segment_row` | boolean int | Aggregated from media-engine `stall`/`stall_recovered` events, then appended when pending row is flushed. | pending methodology | No | Segment-level aggregate only. Final segment stall is suppressed. Event-level stall class remains future work. |
| `stall_duration` | `segment_telemetry.csv` | `player.Player._on_media_event` and `_flush_segment_row` | seconds | Aggregated from media-engine event duration, then appended when pending row is flushed. | pending methodology | No | Do not count terminal drain stalls as steady-state rebuffering. GStreamer queue events are not automatically QoE stalls. |

## `evaluation_segments.csv`

| Column | Artifact | Source module/function | Unit | Timing/source event | Semantic status | Direct benchmark use now? | Notes/risks |
|---|---|---|---|---|---|---|---|
| `segment_index` | `evaluation_segments.csv` | `player.Player._write_evaluation_segment_row` | index | Written after init/download handling for each segment row. | runtime-only | No | Row identity in compact artifact. |
| `is_init` | `evaluation_segments.csv` | `player.Player._write_evaluation_segment_row` | boolean int | Written after init/download handling. | benchmark-neutral; eval-gated | Gate/context only | Init rows are not benchmark rows. |
| `eval_phase` | `evaluation_segments.csv` | `player.Player._compute_derived_features`; `core.benchmark_contract.classify_segment_phase` | label | Written after phase classification. | benchmark-neutral; eval-gated | Gate only | Phase label for eligibility and later filtering. |
| `use_for_eval` | `evaluation_segments.csv` | `player.Player._compute_derived_features`; `core.benchmark_contract.should_use_segment_for_eval` | boolean int | Written after phase classification. | benchmark-neutral; eval-gated | Gate only | `false` means the row is not a benchmark row. |
| `last_fragment_size` | `evaluation_segments.csv` | `player.Player._write_evaluation_segment_row`; downloader result size | bytes | Written after successful media download; init rows write 0. | pending methodology | No | Compact copy without `feedback_` prefix. Throughput/QoE methodology pending. |
| `last_download_time` | `evaluation_segments.csv` | `player.Player._write_evaluation_segment_row`; downloader elapsed time | seconds | Written after successful media download; init rows write 0. | pending methodology | No | Compact copy without `feedback_` prefix. Retry treatment pending. |
| `fragment_duration` | `evaluation_segments.csv` | `player.Player._write_evaluation_segment_row`; parser/player duration context | seconds | Written after segment handling; init rows write 0. | eval-gated | Not as final score | Duration context for later evaluation tooling. |

## Open Provenance Risks

- `bwe` remains a legacy controller key. Its current formula is clear, but the name is ambiguous and should not be used as final bandwidth methodology.
- `cur_bitrate`, `max_bitrate`, and `min_bitrate` store bytes per second despite bitrate-style names.
- `phase_raw` and `phase_smooth` are runtime/debug detector labels, not academic phase labels.
- `stall_flag` and `stall_duration` are segment-level aggregates. Event-level stall provenance and class-specific QoE handling remain pending.
- GStreamer timing and queue behavior are not equivalent to the fake engine. GStreamer headless/fakesink output is structural validation only.
