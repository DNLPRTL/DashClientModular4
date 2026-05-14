# bba Controller API Mapping

## Contract Summary

The future `bba` controller receives current player feedback and returns a target rate in bytes per second. Its decision is a deterministic function of buffer level and the representation ladder.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| playback buffer occupancy | `queued_time` | exists | seconds | seconds | none | media engine feedback, `baseline_entry_contract.md` | fake/GStreamer equivalence is not claimed | use as primary |
| rate map input | `queued_time`, `reservoir_s`, `cushion_s` | derivable | seconds | seconds | normalize within cushion | `source_evidence.md` | deterministic mapping only | derive |
| available bitrates | `rates` | exists | bps in paper context | bytes_per_second_list | compare using client bytes/s values | MPD/client state | ladder order must be valid | use |
| minimum bitrate | `min(rates)` or `min_rate` | derivable/exists | bps | bytes_per_second | none if using client ladder | controller feedback | legacy `min_bitrate` also exists but is alias | use |
| maximum bitrate | `max(rates)` or `max_rate` | derivable/exists | bps | bytes_per_second | none if using client ladder | controller feedback | legacy `max_bitrate` also exists but is alias | use |
| current quality | `level` | exists | representation index | representation_index | none | controller feedback | optional stickiness only | optional |
| capacity estimate | `last_fragment_size / last_download_time` | derivable | bps | bytes_per_second | bytes/time if optional startup guard enabled | source evidence | not main BBA-0 rule | optional/defer |
| segment duration | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | optional safety explanation | optional |
| Netflix production internals | none | forbidden | mixed | none | none | source evidence | not public/local runtime contract | do not use |
| server-side logic | none | forbidden | mixed | none | none | source evidence | client-side baseline only | do not use |
| console output | none | forbidden | text | none | none | runtime console contract | never input | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| target rate | bytes_per_second | `calcControlAction()` | return `rates[target_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | shared quantizer decides final level |

## API Restrictions

- Do not add a throughput dependency for the BBA-0 decision.
- Do not use `queued_bytes` as the primary buffer signal because it is engine-dependent.
- Do not interpret GStreamer queue behavior as benchmark-grade buffer evidence.
- Do not write or mutate run artifacts.
