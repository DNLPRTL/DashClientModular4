# mpc Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `mpc` |
| family | hybrid / model predictive control |
| primary source | Yin et al. 2015, `paper_card.md`, `source_evidence.md` |
| implementation status | future implementation spec; no code in this block |

## Objective

Implement a small-horizon enumerative MPC controller. The controller predicts future throughput from recent segment measurements, enumerates candidate bitrate sequences, simulates buffer evolution, scores each sequence with an internal provisional objective, and returns the first action of the best sequence.

The objective is controller-internal only. It is not the final TFG QoE/reward and must not be used as benchmark scoring.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| bitrate ladder | `rates` | bytes_per_second_list | candidate actions | yes |
| buffer level | `queued_time` | seconds | initial simulated buffer | yes |
| segment duration | `fragment_duration` | seconds | future buffer increment and size approximation | yes |
| last segment size | `last_fragment_size` | bytes | throughput sample numerator | yes for history update |
| last download time | `last_download_time` | seconds | throughput sample denominator | yes for history update |
| current/last quality | `level` | representation_index | switching penalty reference | yes |
| segment index | `segment_index` | index | deterministic context and end-of-video cap if later known | optional |

## Output To DashClientModular4

Return the first representation of the best sequence as `target_rate` in bytes per second. The shared quantizer maps the target rate to a representation index.

## Parameters

| parameter | unit | suggested default | reason/configurability |
| --- | --- | --- | --- |
| `horizon` | chunks | `3` | tractable first implementation; paper-aligned `5` can be configured later |
| `throughput_history_window` | chunks | `5` | paper evidence uses recent chunks for harmonic mean |
| `quality_reward_mode` | enum | `log_rate_ratio` | dimensionless reward independent of absolute units |
| `rebuffer_penalty` | utility_per_second | `4.3` | common MPC/Pensieve-style internal penalty; not final QoE |
| `switch_penalty` | utility_per_utility_delta | `1.0` | discourages avoidable quality jumps |
| `startup_level` | representation_index | `0` | safe fallback with no valid throughput |
| `max_enumerated_sequences` | count | `4096` | prevents combinatorial blow-up |
| `min_valid_throughput_Bps` | bytes_per_second | `0.001` | avoids invalid prediction |

## Formulas

Throughput sample:

```text
throughput_Bps = last_fragment_size_bytes / last_download_time_s
```

Harmonic mean predictor over positive samples:

```text
predicted_Bps = n / sum(1 / throughput_Bps_i for i in recent_positive_samples)
```

Segment-size approximation:

```text
segment_size_bytes(level) = rates[level] * segment_duration_s
```

Buffer simulation:

```text
download_time_s = segment_size_bytes(level) / predicted_Bps
rebuffer_s = max(download_time_s - simulated_buffer_s, 0)
simulated_buffer_s = max(simulated_buffer_s - download_time_s, 0) + segment_duration_s
```

Internal provisional objective:

```text
quality(level) = ln(rates[level] / min_rate)

sequence_score =
    sum(quality(level_t))
    - rebuffer_penalty * sum(rebuffer_s_t)
    - switch_penalty * sum(abs(quality(level_t) - quality(previous_level_t)))
```

This objective is for controller decisions only and is not final evaluation QoE.

## Pseudocode

```text
validate rates
if rates has one entry:
    return rates[0]

if buffer_level_s is missing, negative or non-finite:
    buffer_level_s = 0

if segment_duration_s <= 0:
    return rates[startup_level clamped to ladder]

update throughput history from last_fragment_size / last_download_time when valid
if no positive throughput sample exists:
    return rates[startup_level clamped to ladder]

predicted = harmonic_mean(last throughput_history_window positive samples)
if predicted < min_valid_throughput_Bps:
    return rates[startup_level clamped to ladder]

H = configured horizon
if len(rates) ** H > max_enumerated_sequences:
    reduce H until the limit is satisfied or fail configuration validation

best_score = -infinity
best_first_level = startup_level
for each sequence in product(levels, repeat=H):
    simulated_buffer = buffer_level_s
    previous_level = current level
    score = 0
    for level in sequence:
        size = rates[level] * segment_duration_s
        download_time = size / predicted
        rebuffer = max(download_time - simulated_buffer, 0)
        simulated_buffer = max(simulated_buffer - download_time, 0) + segment_duration_s
        score += quality(level)
        score -= rebuffer_penalty * rebuffer
        score -= switch_penalty * abs(quality(level) - quality(previous_level))
        previous_level = level
    if score > best_score:
        best_score = score
        best_first_level = sequence[0]

return rates[best_first_level]
```

## Edge Cases

| case | required behavior |
| --- | --- |
| empty ladder | validation failure through shared controller contract |
| one-level ladder | return the only rate |
| no throughput history | return startup/min representation |
| zero or negative throughput | ignore sample |
| missing buffer | simulate from `0` seconds |
| missing/non-positive segment duration | startup/min representation |
| horizon too large | reduce horizon within sequence limit or fail config |
| current level invalid | clamp to valid range for switch penalty |
| unknown buffer capacity | do not cap simulated buffer in first implementation |

## Simplifications Accepted

- Online enumeration instead of FastMPC table compression.
- Horizon `3` by default for tractability.
- Harmonic mean throughput prediction.
- Segment-size approximation from bitrate and duration.
- Internal provisional QoE objective for controller decision only.

## Simplifications Prohibited

- No FastMPC lookup tables in the first implementation.
- No external solvers.
- No crowdsourced or future-throughput oracle.
- No fairness or multi-client behavior.
- No final QoE/reward or benchmark scoring.
- No neural/RL implementation.

## Telemetry And Logging Expectations

Future code may expose controller-local debug fields such as `mpc_predicted_throughput_Bps`, `mpc_horizon`, `mpc_best_score`, and `mpc_best_first_level` after provenance is documented. These fields are diagnostic and not benchmark metrics.

## Compatibility With `baseline_entry_contract.md`

- Target rate is bytes per second.
- Representation ladder comes from MPD/client state.
- Quality levels are representation indices.
- Controller decisions do not depend on console output.
- The controller does not mutate CSVs, metrics, parser, downloader, media engine, or evaluation gates.

## Acceptance Criteria

The future implementation must pass `acceptance_tests.md`, keep the internal objective clearly labeled as provisional, and remain deterministic for identical feedback and controller state.

## Risks

- Horizon enumeration can grow quickly with ladder size.
- Segment-size approximation may differ from VBR content.
- Internal objective weights affect behavior and are not final benchmark QoE.
- Prediction from short histories can be unstable during startup.

## Memory/Thesis Usage

Use this spec in Chapter 5 to describe MPC implementation. Chapter 2 should position MPC as the hybrid baseline combining throughput and buffer. Chapter 6 must not treat the internal score as final QoE.
