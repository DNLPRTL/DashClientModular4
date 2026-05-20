# robust_mpc Controller API Mapping

## Contract Summary

The implemented `robust_mpc` controller uses the same API mapping as `mpc` plus deterministic controller-local history for previous robust predictions and actual throughput measurements. It returns a bytes/s target rate for the first action of the best robust sequence.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| available bitrates | `rates` | exists | bitrate ladder | bytes_per_second_list | use client bytes/s directly | MPD/client state | positive ordered ladder required | use |
| selected/current quality | `level` | exists | representation index | representation_index | clamp invalid level | controller feedback | used for switch penalty only | use |
| buffer occupancy | `queued_time` | exists | seconds | seconds | invalid values become `0` | media engine feedback | fake/GStreamer equivalence not claimed | use |
| chunk duration | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | must be positive | use |
| chunk size | `segment_sizes_B` aliases or approximation | derivable | bytes | bytes | exact size when present, else `rates[level] * fragment_duration` | MPC source evidence | disclose VBR limitation | use |
| actual throughput | `last_fragment_size / last_download_time` | derivable | bps or bytes/s | bytes_per_second | bytes/time over valid downloads | downloader/player feedback | invalid samples ignored | derive |
| explicit throughput history | `throughput_history_Bps` aliases | optional | bps or bytes/s | bytes_per_second_list | normalize aliases to bytes/s | controller/test context | positive samples only | use if present |
| base throughput prediction | controller state | derivable | bps or bytes/s | bytes_per_second | harmonic mean of recent positive actual samples | `source_evidence.md` | no future oracle | derive |
| previous predicted throughput | controller state or `predicted_throughput_history_Bps` aliases | derivable/optional | bps or bytes/s | bytes_per_second | stored robust prediction or normalized explicit history | RobustMPC evidence | must align with later actual sample | derive |
| prediction error | controller state or `prediction_error_history` aliases | derivable/optional | ratio | ratio | `abs(predicted - actual) / max(actual, epsilon)` | `source_evidence.md` | use recent window only | derive |
| robust throughput | controller state | derivable | bps or bytes/s | bytes_per_second | `base / (1 + max_error)` or fallback safety factor | RobustMPC evidence | never a final metric | derive |
| horizon | config/controller parameter | derivable/configurable | chunks | chunks | none | implementation spec | sequence limit applies | configure |
| remaining chunks | `remaining_segments` aliases | optional | chunks | chunks | cap horizon when valid | runtime/test context | not required for normal runs | use if present |
| internal objective weights | config/controller parameter | derivable/configurable | utility weights | utility weights | same as MPC | implementation spec | controller-internal only | configure |
| future bandwidth/oracle | `future_bandwidth`, `future_throughput` | forbidden | throughput | none | none | source evidence | no oracle | do not use |
| TCP/network internals | RTT, loss, cwnd | forbidden | mixed | none | none | non-goal | application-layer controller only | do not use |
| server state | server fields | forbidden | mixed | none | none | non-goal | client-side only | do not use |
| Pensieve state vector/model output | Pensieve/RL fields | forbidden | mixed | none | none | Pensieve source artifact | RL controller not implemented | do not use |
| trained neural model | none | forbidden | model | none | none | Pensieve policy | no AI/RL in Phase 2 | do not use |
| ABR server | none | forbidden | service | none | none | non-goal | client-side only | do not use |
| console output | progress/log fields | forbidden | text | none | none | runtime console contract | never input | do not use |
| final QoE/reward | `final_qoe`, `reward` | forbidden | score | none | none | metric validity policy | not defined in Phase 2.3.6 | do not use |

Unit normalization treats `Bps`/`bytes_per_second` as bytes/s, `bps` as bits/s, `kbps` as kilobits/s and `Mbps` as megabits/s. For exact segment sizes, `B` is bytes and `b` is bits.

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| robust first action target rate | bytes_per_second | `calcControlAction()` | return `rates[best_first_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | shared quantizer maps final level |
| additional idle/wait | seconds | `getIdleDuration()` | always `0.0`; no wait action is added |

## API Restrictions

- Do not add Pensieve state, model loading, neural inference, or training.
- Do not persist training data or traces.
- Do not expose internal robust prediction as final benchmark metric.
- Do not modify the MPC/base controller contract to make RobustMPC easier.
- Do not change player, media-engine, metric or artifact behavior.
