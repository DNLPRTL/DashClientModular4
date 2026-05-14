# rate_based Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `rate_based` |
| family | throughput-based / rate-based |
| primary source | Liu et al. 2011, `paper_card.md`, `source_evidence.md` |
| implementation status | future implementation spec; no code in this block |

## Objective

Select the highest representation whose MPD bitrate is below a conservative application-layer throughput estimate. Throughput is the primary signal. Buffer level is used only as a safety guard.

This controller does not define final QoE/reward and does not create benchmark methodology.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| bitrate ladder | `rates` | bytes_per_second_list | candidate representations | yes |
| current quality level | `level` | representation_index | step-wise movement and switch context | yes |
| current representation rate | `cur_rate` or `cur_bitrate` | bytes_per_second | fallback/current-rate context | yes |
| last segment size | `last_fragment_size` | bytes | throughput numerator | yes for measured update |
| last download time | `last_download_time` | seconds | throughput denominator / SFT | yes for measured update |
| segment duration | `fragment_duration` | seconds | MSD explanation and guard defaults | yes |
| buffer level | `queued_time` | seconds | low-buffer safety guard only | yes |
| segment index | `segment_index` | index | deterministic state/debug context | optional |

## Output To DashClientModular4

Return `target_rate` in bytes per second from `calcControlAction()`. The existing quantizer maps it to a representation index. The controller must never write CSV files, change metrics, alter `eval_phase`, or depend on console output.

## Parameters

| parameter | unit | suggested default | reason/configurability |
| --- | --- | --- | --- |
| `safety_factor` | ratio | `0.85` | conservative margin below estimated throughput |
| `ewma_alpha` | ratio | `0.6` | smooths segment-level measurements; configurable for sensitivity |
| `startup_level` | representation_index | `0` | safe startup when no valid measurement exists |
| `critical_buffer_s` | seconds | `max(fragment_duration_s, 2.0)` | buffer guard threshold; derived when segment duration exists |
| `conservative_up` | boolean | `true` | limits upward movement to one level per decision |
| `allow_multi_level_down` | boolean | `true` | supports aggressive decrease after throughput drop |
| `min_valid_download_time_s` | seconds | `0.001` | avoids division by zero and unstable timing |

## Formulas

Instantaneous measured throughput:

```text
throughput_Bps = last_fragment_size_bytes / last_download_time_s
```

EWMA update:

```text
smoothed_Bps = ewma_alpha * throughput_Bps
               + (1 - ewma_alpha) * previous_smoothed_Bps
```

Safe throughput:

```text
safe_Bps = smoothed_Bps * safety_factor
```

Candidate selection:

```text
candidate_level = max(i where rates[i] <= safe_Bps)
target_rate_Bps = rates[candidate_level]
```

The paper's `mu = MSD / SFT` remains an explanatory ratio. The future implementation should use direct bytes/time throughput because the client already exposes size and time in units compatible with the controller contract.

## Pseudocode

```text
validate rates
if rates has one entry:
    return rates[0]

if last_fragment_size <= 0 or last_download_time < min_valid_download_time_s:
    return rates[startup_level clamped to ladder]

instant = last_fragment_size / last_download_time
update smoothed throughput
safe = smoothed * safety_factor
candidate = highest level whose rate <= safe, else level 0

if queued_time is missing, negative or non-finite:
    candidate = min(candidate, current level) if current level is valid else 0

if queued_time <= critical_buffer_s:
    candidate = min(candidate, max(0, current_level - 1))

if conservative_up and candidate > current_level:
    candidate = current_level + 1

if candidate < current_level and allow_multi_level_down:
    keep candidate

return rates[candidate]
```

## Edge Cases

| case | required behavior |
| --- | --- |
| empty ladder | validation failure through shared controller contract |
| one-level ladder | return the only rate |
| no valid measurement | return `startup_level`, default level 0 |
| zero or negative download time | ignore measurement and use startup/safe fallback |
| throughput below minimum | choose minimum representation |
| throughput above maximum | choose maximum, subject to conservative upshift |
| critically low buffer | force minimum or one-step-down safe behavior |
| bit/s vs bytes/s ambiguity | all internal comparisons use bytes per second |

## Simplifications Accepted

- Direct bytes/time throughput instead of explicitly computing `mu`.
- EWMA smoothing instead of a full production estimator.
- Buffer as a guard only, not as the primary rule.
- No TCP-layer instrumentation.

## Simplifications Prohibited

- No TCP RTT, packet loss, congestion window, sender state, server state, or external bandwidth oracle.
- No final QoE/reward definition.
- No replay, trace, emulation, or benchmark claims.
- No runtime/player/metric/config changes as part of this documentation block.

## Telemetry And Logging Expectations

Future code may expose controller-local debug fields only after separate provenance documentation. Minimum useful fields would be `measured_throughput_Bps`, `smoothed_throughput_Bps`, `safe_throughput_Bps`, and `rate_based_candidate_level`. They must not replace canonical run artifacts or console output.

## Compatibility With `baseline_entry_contract.md`

- Target rates are bytes per second.
- Representation ladder comes from MPD/client state through `rates`.
- Quality levels are representation indices.
- Decisions occur at segment boundaries.
- The controller must not write CSVs or mutate evaluation flags.

## Acceptance Criteria

The future implementation is acceptable only if the tests in `acceptance_tests.md` pass, the controller remains deterministic for identical feedback/state, and no forbidden signals are used.

## Risks

- The current `bwe` key is a legacy fallback, so the implementation should prefer explicit size/time updates.
- Segment duration differences from the paper's assumed range can change smoothing behavior.
- A too-high safety factor may oscillate; a too-low factor may be overly conservative.

## Memory/Thesis Usage

Use this spec in Chapter 5 to explain the first academic ABR baseline implementation. In Chapter 2, cite Liu et al. as the source for classical application-layer throughput adaptation. In Chapter 6, use it only after benchmark methodology exists.
