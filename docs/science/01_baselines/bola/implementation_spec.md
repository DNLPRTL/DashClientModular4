# bola Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `bola` |
| family | buffer-based / utility-based / Lyapunov optimization |
| primary source | Spiteri et al. 2020, `paper_card.md`, `source_evidence.md` |
| auxiliary source | Spiteri et al. 2019, `dashjs_source_card.md`, `dashjs_practical_evidence.md` |
| implementation status | implemented in Phase 2.3.4 as BOLA-basic in `core/controller/bola.py` |

## Objective

Implement a reproducible BOLA-basic controller that chooses the representation with the highest BOLA-style score using buffer level, segment duration, representation rates, utility values, segment sizes when available, and documented controller parameters.

This implementation is not dash.js DYNAMIC, not FAST SWITCHING, not BOLA-E, and not production dash.js behavior.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| buffer level | `queued_time` | seconds | primary BOLA state | yes |
| segment duration | `fragment_duration` | seconds | convert buffer to segment units and estimate size | yes |
| bitrate ladder | `rates` | bytes_per_second_list | candidate representations | yes |
| current level | `level` | representation_index | fallback/stickiness context | optional |
| representation size | optional exact keys or approximation | bytes | preferred BOLA denominator | derivable |
| utility per representation | controller-derived | dimensionless | BOLA score | yes |

## Output To DashClientModular4

Return `target_rate` in bytes per second, normally `rates[argmax_score_level]`. The shared quantizer maps it to a representation index.

The current controller API cannot directly express BOLA's no-download/wait option. The first implementation must document this limitation and choose a safe representation when waiting would otherwise be indicated.

## Parameters

| parameter | unit | suggested default | reason/configurability |
| --- | --- | --- | --- |
| `utility_mode` | enum | `log_rate_ratio` | reproducible monotonic utility |
| `size_mode` | enum | `exact_or_bitrate_duration` | use optional exact per-level sizes when supplied; otherwise use approximation |
| `bola_v` / `V` / `v` | controller scale | `5.0` | paper-sensitive parameter; explicit default for reproducible BOLA-basic tests |
| `bola_gamma` / `gamma` | compatible score offset | `0.2` | paper-sensitive parameter; explicit default for reproducible BOLA-basic tests |
| `low_buffer_fallback_s` / `bola_qlow_s` / `qlow_s` | seconds | `segment_duration_s` | select minimum if buffer is below or equal to one segment unless configured |
| `all_negative_policy` | enum | `min_rate` | API cannot express no-download in the first implementation |
| `min_segment_duration_s` | seconds | `0.001` | avoids division by zero |

Invalid or non-positive `bola_v`, `bola_gamma`, and `min_segment_duration_s` fall back to the documented defaults. Unsupported enum values fall back to the documented modes. A later reviewed document may replace these constants with a derivation from intuitive buffer targets such as `q_low_s` and `q_max_s`.

## Formulas

Utility:

```text
utility_m = ln(rate_Bps_m / min_rate_Bps)
```

Segment-size selection:

```text
if exact positive per-level segment sizes are supplied:
    size_bytes_m = exact_size_bytes_m
else:
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

This normalized form keeps the score deterministic when exact segment sizes are unavailable. It is an implementation simplification and must be disclosed. Exact size keys are optional controller-local inputs for tests/future callers; the current player path normally provides only `rates` and `fragment_duration`.

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
    size_units = segment_size_bytes[m] / min_size
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
| empty ladder | safe `0.0` fallback, matching existing controller style |
| one-level ladder | return the only rate |
| missing/negative buffer | select minimum rate |
| segment duration missing or non-positive | select minimum rate |
| zero or negative bitrate | safe `0.0` fallback because the ladder is invalid |
| no exact segment size | use `rate * segment_duration` approximation |
| all scores non-positive | select minimum rate and document no-download limitation |
| invalid `V` or `gamma` | fall back to documented defaults |

## Simplifications Accepted

- BOLA-basic only.
- Log-rate-ratio utility.
- Segment-size approximation from bitrate and duration when exact per-level sizes are absent.
- Normalized size units for deterministic score calculation.
- Minimum-rate fallback for no-download cases.
- Invalid parameter fallback to documented defaults.

## Simplifications Prohibited

- No DYNAMIC.
- No FAST SWITCHING.
- No full production dash.js behavior.
- No BOLA-E unless a later source mapping promotes it.
- No throughput prediction as primary BOLA input.
- No live-specific low-latency behavior.
- No final QoE/reward definition.

## Telemetry And Logging Expectations

The implementation exposes controller-local `last_metrics` fields such as `scores_by_level`, `raw_best_level`, `q_segments`, `bola_v`, and `bola_gamma`. These values are diagnostic, not canonical telemetry and not final benchmark metrics.

## Compatibility With `baseline_entry_contract.md`

- Return target rates in bytes per second.
- Use MPD/client ladder from `rates`.
- Treat quality levels as representation indices.
- Do not modify output artifacts, metrics, parser, downloader, media engine, or configs.
- Do not depend on console output.

## Acceptance Criteria

The implementation must pass `acceptance_tests.md`, must document its `bola_v`/`bola_gamma` configuration, and must clearly label itself BOLA-basic rather than dash.js DYNAMIC or production BOLA-E.

## Risks

- BOLA parameter calibration is sensitive and not finalized here.
- The no-download/wait option is not expressible in the first controller contract.
- Segment-size approximation may differ from real VBR segment sizes.
- Production dash.js adaptations are intentionally deferred.

## Memory/Thesis Usage

Use this spec in Chapter 5 to explain the BOLA-basic implementation and limitations. In Chapter 2, present BOLA as a utility/Lyapunov buffer-based method. In Chapter 6, compare only after evaluation methodology exists.
