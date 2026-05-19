# bba Controller API Mapping

## Contract Summary

`bba` uses the current dict-based controller API:

- `setPlayerFeedback(feedback_dict)` receives runtime feedback.
- `calcControlAction()` returns a target rate in bytes per second.
- `quantizeRate(target_rate)` maps that target rate to a representation index.
- `getIdleDuration()` remains `0.0`; BBA does not pace downloads.

## Signal Mapping

| paper concept | DashClientModular4 signal | status | paper unit | client unit | conversion / use | decision |
| --- | --- | --- | --- | --- | --- | --- |
| playback buffer occupancy | `queued_time` | exists | seconds | seconds | used directly as `buffer_level_s` | use as primary |
| reservoir | `reservoir_s` controller parameter | implemented | seconds | seconds | low-buffer threshold | use |
| cushion | `cushion_s` controller parameter | implemented | seconds | seconds | ramp interval above reservoir | use |
| available bitrates | `rates` | exists | bps in paper context | bytes_per_second_list | compare and emit in bytes/s through client ladder | use |
| maximum selectable level | `max_level` | exists | representation index | representation_index | clamps ladder before selection | use |
| minimum bitrate | `rates[0]` after clamp | derivable | bps | bytes_per_second | output when buffer is invalid or low | use |
| maximum bitrate | `rates[-1]` after clamp | derivable | bps | bytes_per_second | output when buffer is above reservoir+cushion | use |
| current quality | `level` | exists | representation index | representation_index | context only in BBA-0 | optional/deferred |
| capacity estimate | `bwe`, `last_fragment_size / last_download_time` | exists/derivable | bps or B/s | bytes_per_second | not used by BBA-0 decision | defer |
| segment duration | `fragment_duration` | exists | seconds | seconds | explanatory/safety context only | optional |
| TCP RTT | none | forbidden | seconds | none | no TCP-layer instrumentation | do not use |
| packet loss | none | forbidden | count/ratio | none | no TCP-layer dependency | do not use |
| congestion window | none | forbidden | bytes/packets | none | no TCP-layer dependency | do not use |
| server/sender state | none | forbidden | mixed | none | client-side controller only | do not use |
| external/future bandwidth oracle | none | forbidden | mixed | none | no future oracle | do not use |
| console/log/progress text | none | forbidden | text | none | non-canonical runtime output | do not use |
| final QoE/reward | none | forbidden | score | none | not defined in Phase 2.3.3 | do not use |
| GStreamer-only observations | none | forbidden | mixed | none | integration/demo path only | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| target rate | bytes_per_second | `calcControlAction()` | return `rates[target_level]`, or `0.0` only for invalid/no ladder |
| chosen quality | representation_index | `quantizeRate(target_rate)` | representation index after shared quantization |

## BBA-0 Mapping

```text
if queued_time <= reservoir_s:
    level = 0
elif queued_time >= reservoir_s + cushion_s:
    level = max_level
else:
    x = (queued_time - reservoir_s) / cushion_s
    level = floor(x * max_level)
```

The implementation compares only seconds and representation indices. No throughput unit conversion is required for the BBA decision. The returned ladder rate is already in bytes per second because `Player` converts MPD `bandwidth` to `rates` in bytes/s.

## API Restrictions Preserved

- No new feedback keys are required.
- No parser, downloader, player, media-engine, metric, or output-artifact contract changes are required.
- No canonical telemetry columns are added by the controller.
- `queued_bytes` is not used as the primary buffer signal because it is engine-dependent.
- Fake smoke output is integration evidence, not benchmark evidence.
