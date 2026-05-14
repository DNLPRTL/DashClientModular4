# robust_mpc Controller API Mapping

## Contract Summary

The future `robust_mpc` controller uses the same API mapping as `mpc` plus deterministic controller-local history for previous predictions and actual throughput measurements.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| available bitrates | `rates` | exists | bitrate ladder | bytes_per_second_list | use client bytes/s directly | MPD/client state | positive ordered ladder required | use |
| buffer occupancy | `queued_time` | exists | seconds | seconds | none | media engine feedback | fake/GStreamer equivalence not claimed | use |
| chunk duration | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | must be positive | use |
| chunk size | no per-future-size matrix | derivable | bytes | bytes | `rates[level] * fragment_duration` | MPC source evidence | approximation; disclose VBR limitation | derive |
| actual throughput | `last_fragment_size / last_download_time` | derivable | bps or bytes/s | bytes_per_second | bytes/time over valid downloads | downloader/player feedback | invalid samples ignored | derive |
| base throughput prediction | controller state | derivable | bps or bytes/s | bytes_per_second | harmonic mean of recent positive actual samples | `source_evidence.md` | no future oracle | derive |
| previous predicted throughput | controller state | derivable | bps or bytes/s | bytes_per_second | store prediction made for previous chunk | RobustMPC evidence | must align with later actual sample | derive |
| prediction error | controller state | derivable | percentage/ratio | ratio | `abs(predicted - actual) / max(actual, epsilon)` | `source_evidence.md` | use recent window only | derive |
| robust throughput | controller state | derivable | bps or bytes/s | bytes_per_second | `base / (1 + max_error)` | RobustMPC evidence | fallback to safety factor if no error history | derive |
| horizon | config/controller parameter | derivable/configurable | chunks | chunks | none | implementation spec | sequence limit applies | configure |
| internal QoE weights | config/controller parameter | derivable/configurable | utility weights | utility weights | same as MPC | implementation spec | controller-internal only | configure |
| Pensieve state vector | none | forbidden | mixed | none | none | Pensieve source artifact | RL controller not implemented | do not use |
| trained neural model | none | forbidden | model | none | none | Pensieve policy | no AI/RL in Phase 2 | do not use |
| ABR server | none | forbidden | service | none | none | non-goal | client-side only | do not use |
| console output | none | forbidden | text | none | none | runtime console contract | never input | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| robust first action target rate | bytes_per_second | `calcControlAction()` | return `rates[best_first_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | shared quantizer maps final level |

## API Restrictions

- Do not add Pensieve state, model loading, neural inference, or training.
- Do not persist training data or traces.
- Do not expose internal robust prediction as final benchmark metric.
- Do not modify the MPC/base controller contract to make RobustMPC easier.
