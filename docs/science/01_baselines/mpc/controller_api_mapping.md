# mpc Controller API Mapping

## Contract Summary

The implemented `mpc` controller receives segment-boundary feedback, keeps deterministic controller-local throughput history, and returns the target rate for the first action of the best planned sequence.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| available bitrates | `rates` | exists | bitrate ladder | bytes_per_second_list | use client bytes/s directly | MPD/client state | positive ordered ladder required | use |
| selected/current bitrate | `level`, `cur_rate` | exists | representation index/rate | representation_index, bytes_per_second | `level` for switch penalty; clamp invalid level | controller feedback | `cur_rate` is context only | use `level` |
| buffer occupancy | `queued_time` | exists | seconds | seconds | invalid values become `0` | media engine feedback | fake/GStreamer equivalence not claimed | use |
| chunk duration | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | must be positive | use |
| chunk size | `segment_sizes_B` aliases or approximation | derivable | bytes | bytes | exact size when present, else `rates[level] * fragment_duration` | implementation spec | disclose VBR limitation | use |
| past throughput | `last_fragment_size / last_download_time` | derivable | bps or bytes/s | bytes_per_second | bytes/time; ignore invalid samples | downloader/player feedback | controller state stores recent samples | derive |
| explicit throughput history | `throughput_history_Bps` aliases | optional | bps or bytes/s | bytes_per_second_list | normalize aliases to bytes/s | test/runtime extension context | positive samples only | use if present |
| explicit measured throughput | `measured_throughput_Bps` aliases | optional | bps or bytes/s | bytes_per_second | normalize aliases to bytes/s | test/runtime extension context | positive samples only | use if present |
| throughput prediction | controller state | derivable | bps or bytes/s | bytes_per_second | harmonic mean of recent positive samples | `source_evidence.md` | no future oracle | derive |
| horizon | config/controller parameter | derivable/configurable | chunks | chunks | none | implementation spec | bounded by sequence limit | configure |
| remaining chunks | `remaining_segments` aliases | optional | chunks | chunks | cap horizon when valid | runtime/test context | not required for normal runs | use if present |
| internal quality reward | controller formula | derivable | utility | dimensionless | `ln(rate/min_rate)` | implementation spec | not final QoE | derive |
| rebuffer penalty | config/controller parameter | derivable/configurable | utility/second | utility_per_second | none | implementation spec | internal only | configure |
| switching penalty | config/controller parameter | derivable/configurable | utility delta | utility_per_utility_delta | none | implementation spec | internal only | configure |
| future bandwidth | `future_bandwidth`, `future_throughput` | forbidden | throughput | none | none | source evidence | no oracle | do not use |
| TCP/network internals | RTT, loss, cwnd | forbidden | mixed | none | none | non-goal | application-layer controller only | do not use |
| external solver | none | forbidden | mixed | none | none | non-goal | enumeration only first | do not use |
| console output | progress/log fields | forbidden | text | none | none | runtime console contract | never input | do not use |
| final QoE/reward | `final_qoe`, `reward` | forbidden | score | none | none | metric validity policy | not defined in Phase 2.3.5 | do not use |
| neural/RL state | Pensieve/RL fields | forbidden | mixed | none | none | non-goal | no AI/RL | do not use |

Unit normalization treats `Bps`/`bytes_per_second` as bytes/s, `bps` as bits/s, `kbps` as kilobits/s and `Mbps` as megabits/s. For exact segment sizes, `B` is bytes and `b` is bits.

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| first action target rate | bytes_per_second | `calcControlAction()` | return `rates[best_first_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | shared quantizer maps final level |
| additional idle/wait | seconds | `getIdleDuration()` | always `0.0`; no MPC wait action is added |

## API Restrictions

- Do not write the internal objective into final metric definitions.
- Do not add replay/emulation or trace dependencies in this controller block.
- Do not change the player scheduling loop.
- Do not treat GStreamer integration output as benchmark-grade.
- Do not implement RobustMPC prediction-error correction in the `mpc` controller.
