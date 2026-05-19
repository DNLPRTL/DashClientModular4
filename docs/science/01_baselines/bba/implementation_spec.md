# bba Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `bba` |
| family | buffer-based ABR |
| primary source | Huang et al. 2014, `paper_card.md`, `source_evidence.md` |
| implementation status | implemented in Phase 2.3.3 as the second academic ABR baseline after `rate_based` |
| code module | `core/controller/bba.py` |
| test module | `tests/test_bba_controller.py` |

## Objective

`bba` implements a deterministic BBA-0-style reservoir/cushion buffer map. Playback buffer level is the primary decision signal. This controller is intentionally not throughput-based.

Throughput/capacity estimation is deferred as an optional startup extension. It is not used in the Phase 2.3.3 BBA-0 decision rule.

## Inputs From DashClientModular4

| input | client key | unit | role | status |
| --- | --- | --- | --- | --- |
| buffer level | `queued_time` | seconds | primary BBA state | required with safe fallback |
| representation ladder | `rates` | bytes_per_second_list | candidate actions | required |
| maximum selectable level | `max_level` | representation_index | clamps the ladder to available levels | required with safe fallback |
| current level | `level` | representation_index | context only; no stickiness in BBA-0 | optional |
| representation bitrate | `rates[i]` | bytes_per_second | returned target rate | required |

## Outputs To DashClientModular4

`calcControlAction()` returns `target_rate` in bytes per second. `quality_level` remains the representation index produced by `quantizeRate(target_rate)`.

The controller does not write CSV files, mutate evaluation gates, parse console output, download segments, parse MPDs, or alter metrics.

## Parameters

| parameter | default | unit | implementation note |
| --- | ---: | --- | --- |
| `reservoir_s` | `5.0` | seconds | low-buffer region where minimum representation is selected |
| `cushion_s` | `10.0` | seconds | ramp interval from minimum to maximum representation |

Both parameters are configurable through existing `controller.params`. Invalid values are sanitized to defaults:

- `reservoir_s < 0`, non-numeric or non-finite -> `5.0`;
- `cushion_s <= 0`, non-numeric or non-finite -> `10.0`.

No new config schema or runtime plumbing was added.

## BBA-0 Buffer Map

Thresholds:

```text
low_threshold_s = reservoir_s
high_threshold_s = reservoir_s + cushion_s
```

Decision rule:

```text
if no valid ladder:
    return 0.0

if one representation:
    return rates[0]

if buffer_level_s is missing, negative or non-finite:
    target_level = 0
elif buffer_level_s <= reservoir_s:
    target_level = 0
elif buffer_level_s >= reservoir_s + cushion_s:
    target_level = len(rates) - 1
else:
    x = (buffer_level_s - reservoir_s) / cushion_s
    target_level = floor(x * (len(rates) - 1))

return rates[target_level]
```

The intermediate cushion mapping is deterministic and discrete. For rates `[100, 200, 400, 800]`, `reservoir_s=5.0` and `cushion_s=10.0`:

- buffer `<= 5.0` selects level `0`;
- buffer `10.0` selects level `1`;
- buffer `14.9` selects level `2`;
- buffer `>= 15.0` selects level `3`.

## Edge Cases

| case | behavior |
| --- | --- |
| empty or missing ladder | return `0.0` without crashing |
| malformed or non-positive ladder | return `0.0` without crashing |
| one-level ladder | return index `0` |
| missing buffer | select minimum representation |
| negative/non-finite buffer | select minimum representation |
| buffer exactly `reservoir_s` | select minimum representation |
| buffer exactly `reservoir_s + cushion_s` | select maximum representation |
| very large buffer | select maximum representation |
| `max_level` below ladder max | select only within available levels |
| invalid reservoir/cushion config | use documented defaults |

## Forbidden Signals

The implementation intentionally does not use TCP RTT, packet loss, congestion window, sender/server state, external or future bandwidth oracles, console/log/progress text, final QoE/reward, replay traces, GStreamer-only observations, or throughput as the primary decision signal.

## Compatibility With `baseline_entry_contract.md`

- Representation ladder comes from MPD/client state through `rates`.
- Target rates are bytes per second.
- Quality levels are representation indices.
- The controller does not alter parser, downloader, player, media engine, metrics, configs, output artifacts, or evaluation gates.

## Validation Status

Phase 2.3.3 validation consists of:

- unit tests in `tests/test_bba_controller.py`;
- full `python -m unittest discover`;
- strict client readiness check;
- fake-engine smoke run through the current CLI/config path.

The fake smoke run validates integration and artifact production only. It is not a benchmark and does not prove BBA is better or worse than `rate_based`, BOLA, MPC or RobustMPC.

## Memory/Thesis Usage

Use this spec in Chapter 5 as the operational description of the BBA-0 implementation. In Chapter 2, cite Huang et al. as the buffer-based ABR source. In Chapter 6, compare only after final methodology, traces/replay and QoE/reward are defined.
