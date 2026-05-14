# bola Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `bola` |
| family | buffer-based / utility-based / Lyapunov optimization |
| primary source | Spiteri et al. 2020, `paper_card.md`, `source_evidence.md` |
| auxiliary source | Spiteri et al. 2019, `dashjs_source_card.md`, `dashjs_practical_evidence.md` |
| implementation status | future BOLA-basic implementation spec; no code in this block |

## Objective

Implement a reproducible BOLA-basic controller that chooses the representation with the highest BOLA-style score using buffer level, segment duration, representation rates, utility values, and documented controller parameters.

This implementation is not dash.js DYNAMIC, not FAST SWITCHING, not BOLA-E, and not production dash.js behavior.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| buffer level | `queued_time` | seconds | primary BOLA state | yes |
| segment duration | `fragment_duration` | seconds | convert buffer to segment units and estimate size | yes |
| bitrate ladder | `rates` | bytes_per_second_list | candidate representations | yes |
| current level | `level` | representation_index | fallback/stickiness context | optional |
| representation size | not directly available | bytes | preferred BOLA denominator | derivable |
| utility per representation | controller-derived | dimensionless | BOLA score | yes |

## Output To DashClientModular4

Return `target_rate` in bytes per second, normally `rates[argmax_score_level]`. The shared quantizer maps it to a representation index.

The current controller API cannot directly express BOLA's no-download/wait option. The first implementation must document this limitation and choose a safe representation when waiting would otherwise be indicated.

## Parameters

| parameter | unit | suggested default | reason/configurability |
| --- | --- | --- | --- |
| `utility_mode` | enum | `log_rate_ratio` | reproducible monotonic utility |
| `size_mode` | enum | `bitrate_times_duration` | exact per-segment sizes are not currently exposed |
| `V` | controller scale | configurable, fixture default `5.0` for tests | paper-sensitive parameter; production default must be reviewed |
| `gamma` | compatible score offset | configurable, fixture default `0.2` for tests | paper-sensitive parameter; production default must be reviewed |
| `low_buffer_fallback_s` | seconds | `segment_duration_s` | select minimum if buffer is below one segment |
| `all_negative_policy` | enum | `min_rate` | API cannot express no-download in the first implementation |
| `min_segment_duration_s` | seconds | `0.001` | avoids division by zero |

`V` and `gamma` must remain explicit configuration or be derived in a later reviewed document from intuitive buffer targets such as `q_low_s` and `q_max_s`. The fixture defaults above are for deterministic unit tests only.

## Formulas

Utility:

```text
utility_m = ln(rate_Bps_m / min_rate_Bps)
```

Segment-size approximation:

```text
size_bytes_m = rate_Bps_m * segment_duration_s
size_units_m = size_bytes_m / min_size_bytes
```

Buffer in segment units:

```text
Q_segments = buffer_level_s / segment_duration_s
```

BOLA-basic score used for the first implementation:

```text
score_m = (V * (utility_m + gamma * segment_duration_s) - Q_segments) / size_units_m
```

This normalized form keeps the score deterministic when exact segment sizes are unavailable. It is an implementation simplification and must be disclosed.

## Pseudocode

```text
validate rates
if rates has one entry:
    return rates[0]

if buffer_level_s is missing, negative or non-finite:
    return min(rates)

if segment_duration_s < min_segment_duration_s:
    return min(rates)

if buffer_level_s <= low_buffer_fallback_s:
    return min(rates)

min_rate = min(rates)
min_size = min_rate * segment_duration_s
Q = buffer_level_s / segment_duration_s

best_level = 0
best_score = -infinity
for each level m:
    utility = ln(rates[m] / min_rate)
    size_units = (rates[m] * segment_duration_s) / min_size
    score = (V * (utility + gamma * segment_duration_s) - Q) / size_units
    if score > best_score:
        best_score = score
        best_level = m

if best_score <= 0 and all_negative_policy == min_rate:
    best_level = 0

return rates[best_level]
```

## Edge Cases

| case | required behavior |
| --- | --- |
| empty ladder | validation failure through shared controller contract |
| one-level ladder | return the only rate |
| missing/negative buffer | select minimum rate |
| segment duration missing or non-positive | select minimum rate |
| zero or negative bitrate | validation failure through shared controller contract |
| no exact segment size | use `rate * segment_duration` approximation |
| all scores non-positive | select minimum rate and document no-download limitation |
| invalid `V` or `gamma` | configuration validation failure in future implementation |

## Simplifications Accepted

- BOLA-basic only.
- Log-rate-ratio utility.
- Segment-size approximation from bitrate and duration.
- Normalized size units for deterministic score calculation.
- Minimum-rate fallback for no-download cases.

## Simplifications Prohibited

- No DYNAMIC.
- No FAST SWITCHING.
- No full production dash.js behavior.
- No BOLA-E unless a later source mapping promotes it.
- No throughput prediction as primary BOLA input.
- No live-specific low-latency behavior.
- No final QoE/reward definition.

## Telemetry And Logging Expectations

Future code may expose controller-local debug fields such as `bola_score_by_level`, `bola_best_level`, `bola_q_segments`, `bola_v`, and `bola_gamma` only after provenance is documented. These values are diagnostic, not final benchmark metrics.

## Compatibility With `baseline_entry_contract.md`

- Return target rates in bytes per second.
- Use MPD/client ladder from `rates`.
- Treat quality levels as representation indices.
- Do not modify output artifacts, metrics, parser, downloader, media engine, or configs.
- Do not depend on console output.

## Acceptance Criteria

The future implementation must pass `acceptance_tests.md`, must document its `V`/`gamma` configuration, and must clearly label itself BOLA-basic rather than dash.js DYNAMIC or production BOLA-E.

## Risks

- BOLA parameter calibration is sensitive and not finalized here.
- The no-download/wait option is not expressible in the first controller contract.
- Segment-size approximation may differ from real VBR segment sizes.
- Production dash.js adaptations are intentionally deferred.

## Memory/Thesis Usage

Use this spec in Chapter 5 to explain the BOLA-basic implementation and limitations. In Chapter 2, present BOLA as a utility/Lyapunov buffer-based method. In Chapter 6, compare only after evaluation methodology exists.
