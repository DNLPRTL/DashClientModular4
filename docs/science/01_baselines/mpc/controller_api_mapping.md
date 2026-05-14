# mpc Controller API Mapping

## Contract Summary

The future `mpc` controller receives segment-boundary feedback, keeps deterministic controller-local history, and returns the target rate for the first action of the best planned sequence.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| available bitrates | `rates` | exists | bitrate ladder | bytes_per_second_list | use client bytes/s directly | MPD/client state | positive ordered ladder required | use |
| selected/current bitrate | `level`, `cur_rate` | exists | representation index/rate | representation_index, bytes_per_second | `level` for switch penalty; `cur_rate` for context | controller feedback | clamp invalid level in future implementation | use |
| buffer occupancy | `queued_time` | exists | seconds | seconds | none | media engine feedback | fake/GStreamer equivalence not claimed | use |
| chunk duration | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | must be positive | use |
| chunk size | no per-future-size matrix | derivable | bytes | bytes | `rates[level] * fragment_duration` | `source_evidence.md` | approximation; disclose VBR limitation | derive |
| past throughput | `last_fragment_size / last_download_time` | derivable | bps or bytes/s | bytes_per_second | bytes/time; ignore invalid samples | downloader/player feedback | controller state stores history | derive |
| throughput prediction | controller state | derivable | bps or bytes/s | bytes_per_second | harmonic mean of recent positive samples | `source_evidence.md` | no future oracle | derive |
| horizon | config/controller parameter | derivable/configurable | chunks | chunks | none | implementation spec | bounded by sequence limit | configure |
| internal quality reward | controller formula | derivable | utility | dimensionless | `ln(rate/min_rate)` by default | implementation spec | not final QoE | derive |
| rebuffer penalty | config/controller parameter | derivable/configurable | utility/second | utility_per_second | none | implementation spec | internal only | configure |
| switching penalty | config/controller parameter | derivable/configurable | utility delta | utility_per_utility_delta | none | implementation spec | internal only | configure |
| remaining chunks | not currently required | missing/optional | chunks | none | none | source evidence | horizon not capped by remaining chunks initially | defer |
| future bandwidth | none | forbidden | throughput | none | none | source evidence | no oracle | do not use |
| external solver | none | forbidden | mixed | none | none | non-goal | enumeration only first | do not use |
| console output | none | forbidden | text | none | none | runtime console contract | never input | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| first action target rate | bytes_per_second | `calcControlAction()` | return `rates[best_first_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | shared quantizer maps final level |

## API Restrictions

- Do not write the internal objective into final metric definitions.
- Do not add replay/emulation or trace dependencies in this controller spec.
- Do not change the player scheduling loop.
- Do not treat GStreamer integration output as benchmark-grade.
