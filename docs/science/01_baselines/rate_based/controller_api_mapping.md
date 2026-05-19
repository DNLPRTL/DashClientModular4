# rate_based Controller API Mapping

## Contract Summary

`rate_based` uses the current dict-based controller API:

- `setPlayerFeedback(feedback_dict)` receives the latest runtime feedback.
- `calcControlAction()` returns a target rate in bytes per second.
- `quantizeRate(target_rate)` maps that rate to a representation index.
- `getIdleDuration()` remains `0.0`; the controller does not pace downloads.

## Signal Mapping

| paper concept | DashClientModular4 signal | status | paper unit | client unit | conversion / use | decision |
| --- | --- | --- | --- | --- | --- | --- |
| available bitrates | `rates` | exists | bps in DASH literature | bytes_per_second_list | compare in bytes/s; `rates_unit=bps` is converted only when explicitly provided | use |
| current representation | `level` | exists | representation index | representation_index | clamp to ladder; fallback to last selected/startup if missing | use |
| current bitrate | `cur_rate`, `cur_bitrate` | exists | bps in literature | bytes_per_second | used only as context when needed; names are legacy aliases | use with caution |
| measured throughput | `bwe`, `measured_throughput*`, `throughput*` | exists/derivable | bps or B/s | bytes_per_second | explicit `bps`/`kbps` suffixes convert to bytes/s; plain `bwe` is bytes/s | use |
| segment fetch time (SFT) | `last_download_time` | exists | seconds | seconds | must be positive; zero/negative is invalid | use |
| segment size | `last_fragment_size` | exists | bytes/bits by paper notation | bytes | direct implementation uses `bytes / seconds` | use |
| media segment duration (MSD) | `fragment_duration` | exists | seconds | seconds | documents the Liu ratio; not needed for bytes/time throughput | use as context |
| smoothed throughput | controller EWMA state | derivable | bps | bytes_per_second | deterministic EWMA with `ewma_alpha=0.5` by default | derive |
| throughput history | `throughput_history*` | optional | bps or B/s | bytes_per_second | positive values only; explicit suffix converts units | optional |
| buffer guard | `queued_time` | exists | seconds | seconds | low buffer can only lower/hold the selected level | use as guard |
| TCP RTT | none | forbidden | seconds | none | no TCP-layer instrumentation | do not use |
| packet loss | none | forbidden | count/ratio | none | no TCP-layer dependency | do not use |
| congestion window | none | forbidden | bytes/packets | none | no TCP-layer dependency | do not use |
| server/sender state | none | forbidden | mixed | none | receiver-side controller only | do not use |
| external bandwidth oracle | none | forbidden | mixed | none | no future oracle | do not use |
| console/log/progress text | none | forbidden | text | none | runtime console is non-canonical | do not use |
| final QoE/reward | none | forbidden | score | none | not defined in Phase 2.3.2 | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| target rate | bytes_per_second | `calcControlAction()` | return a ladder rate in bytes/s, or `0.0` only for invalid/no ladder |
| chosen quality | representation_index | `quantizeRate(target_rate)` | representation index after shared quantization |

## Unit Conversions

```text
bitrate_bps = bitrate_kbps * 1000
bitrate_Bps = bitrate_bps / 8
throughput_Bps = last_fragment_size_bytes / last_download_time_s
throughput_bps = 8 * throughput_Bps
safe_throughput_Bps = throughput_Bps * safety_factor
```

The implemented comparison is always in bytes per second.

## API Restrictions Preserved

- No new feedback keys are required.
- No parser, downloader, player, media-engine, metric, or output-artifact contract changes are required.
- No canonical telemetry columns are added by the controller.
- The controller does not depend on `start_segment_request` or `stop_segment_request`; those remain diagnostics.
- Fake smoke output is integration evidence, not benchmark evidence.
