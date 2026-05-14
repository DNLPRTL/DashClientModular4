# bba Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `bba` |
| family | buffer-based |
| primary source | Huang et al. 2014, `paper_card.md`, `source_evidence.md` |
| implementation status | future implementation spec; no code in this block |

## Objective

Implement a simple BBA-0-style buffer-map controller. Buffer level is the primary decision signal. Throughput is optional startup context only and is not required in the first implementation.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| buffer level | `queued_time` | seconds | primary state | yes |
| bitrate ladder | `rates` | bytes_per_second_list | candidate representations | yes |
| current level | `level` | representation_index | optional stickiness/debug | optional |
| min representation | derived from `rates` | representation_index | low-buffer fallback | yes |
| max representation | derived from `rates` | representation_index | high-buffer selection | yes |
| segment duration | `fragment_duration` | seconds | optional safety discussion | optional |

## Output To DashClientModular4

Return `target_rate` in bytes per second, usually `rates[target_level]`. The shared quantizer converts the target rate to a representation index.

## Parameters

| parameter | unit | suggested default | reason/configurability |
| --- | --- | --- | --- |
| `reservoir_s` | seconds | `5.0` | low-buffer region where minimum rate is selected; configurable |
| `cushion_s` | seconds | `10.0` | ramp interval from min to max; must be `> 0` |
| `mapping_mode` | enum | `threshold_floor` | deterministic discrete mapping to ladder |
| `invalid_buffer_policy` | enum | `min_rate` | safe fallback for missing/invalid buffer |
| `startup_throughput_guard` | boolean | `false` | optional future extension, off for BBA-0 |

## Formulas

Low and high thresholds:

```text
low_threshold_s = reservoir_s
high_threshold_s = reservoir_s + cushion_s
```

Intermediate normalized position:

```text
x = clamp((buffer_level_s - reservoir_s) / cushion_s, 0, 1)
target_level = floor(x * (num_levels - 1))
```

The output target rate is:

```text
target_rate_Bps = rates[target_level]
```

## Pseudocode

```text
validate rates
if rates has one entry:
    return rates[0]

if reservoir_s < 0 or cushion_s <= 0:
    fail configuration validation in future implementation

if buffer_level_s is missing, negative or non-finite:
    return min(rates)

if buffer_level_s <= reservoir_s:
    return min(rates)

if buffer_level_s >= reservoir_s + cushion_s:
    return max(rates)

x = (buffer_level_s - reservoir_s) / cushion_s
target_level = floor(x * (len(rates) - 1))
return rates[target_level]
```

## Edge Cases

| case | required behavior |
| --- | --- |
| empty ladder | validation failure through shared controller contract |
| one-level ladder | return the only rate |
| missing buffer | select minimum rate |
| negative buffer | select minimum rate |
| buffer exactly `reservoir_s` | select minimum rate |
| buffer exactly `reservoir_s + cushion_s` | select maximum rate |
| `cushion_s <= 0` | invalid configuration |
| very large buffer | select maximum rate |

## Simplifications Accepted

- BBA-0-style deterministic map.
- Linear/threshold mapping over the discrete ladder.
- No startup throughput estimator in the first implementation.
- No VBR-specific production tuning.

## Simplifications Prohibited

- Do not make throughput the main decision signal.
- Do not implement Netflix production internals.
- Do not define final QoE/reward.
- Do not add server-side behavior, user/device tuning, replay, or benchmark code.
- Do not depend on console output.

## Telemetry And Logging Expectations

Future code may expose controller-local debug fields such as `bba_buffer_s`, `bba_reservoir_s`, `bba_cushion_s`, and `bba_target_level` only after provenance is documented. The controller must not write canonical CSV artifacts directly.

## Compatibility With `baseline_entry_contract.md`

- The ladder comes from MPD/client state through `rates`.
- The target rate is bytes per second.
- Quality level is a representation index.
- The controller does not alter parser, downloader, media engine, metrics, configs, or evaluation gates.

## Acceptance Criteria

The future implementation must pass all tests in `acceptance_tests.md`, especially threshold behavior and invalid-buffer fallback.

## Risks

- Reservoir/cushion defaults are not Netflix production values.
- Linear mapping may differ from paper-specific discrete barriers.
- BBA-0 may be less responsive during startup because throughput guard is disabled.

## Memory/Thesis Usage

Use this spec in Chapter 5 as the operational description of a simple BBA-0 implementation. In Chapter 2, cite Huang et al. as the buffer-based source. In Chapter 6, present comparisons only after evaluation methodology exists.
