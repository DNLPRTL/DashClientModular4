# robust_mpc Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `robust_mpc` |
| family | hybrid / robust model predictive control |
| primary sources | Yin et al. 2015, Mao et al. 2017, `paper_card.md`, `source_evidence.md`, `pensieve_source_artifact_card.md` |
| implementation status | future implementation spec; no code in this block |

## Objective

Implement RobustMPC as MPC with a conservative throughput prediction. The controller computes the same MPC enumeration and internal objective as `mpc`, but reduces the predicted throughput using recent prediction errors when those errors are available.

This is not Pensieve, not RL, not neural inference, and not final QoE/reward.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| bitrate ladder | `rates` | bytes_per_second_list | candidate actions | yes |
| buffer level | `queued_time` | seconds | initial simulated buffer | yes |
| segment duration | `fragment_duration` | seconds | buffer simulation and size approximation | yes |
| last segment size | `last_fragment_size` | bytes | actual throughput sample | yes for history update |
| last download time | `last_download_time` | seconds | actual throughput sample | yes for history update |
| current/last quality | `level` | representation_index | switching penalty reference | yes |
| previous predicted throughput | controller state | bytes_per_second | prediction error calculation | required when available |
| actual throughput history | controller state | bytes_per_second_list | base prediction and error history | yes |

## Output To DashClientModular4

Return the first representation of the best robust sequence as `target_rate` in bytes per second. The shared quantizer maps it to a representation index.

## Parameters

| parameter | unit | suggested default | reason/configurability |
| --- | --- | --- | --- |
| `horizon` | chunks | `3` | tractable first implementation; paper-aligned `5` can be configured later |
| `throughput_history_window` | chunks | `5` | harmonic mean base predictor window |
| `prediction_error_window` | chunks | `5` | robust correction window from source evidence |
| `startup_safety_factor` | ratio | `0.85` | conservative fallback when prediction errors are unavailable |
| `epsilon_throughput_Bps` | bytes_per_second | `0.001` | avoids division by zero in percentage error |
| `quality_reward_mode` | enum | `log_rate_ratio` | same as MPC |
| `rebuffer_penalty` | utility_per_second | `4.3` | internal controller objective only |
| `switch_penalty` | utility_per_utility_delta | `1.0` | internal controller objective only |
| `max_enumerated_sequences` | count | `4096` | prevents combinatorial blow-up |

## Formulas

Base prediction is the MPC harmonic mean:

```text
base_prediction_Bps =
    n / sum(1 / throughput_Bps_i for i in recent_positive_samples)
```

Prediction error for a past chunk:

```text
error_i = abs(predicted_Bps_i - actual_Bps_i) / max(actual_Bps_i, epsilon_throughput_Bps)
```

Recent maximum error:

```text
err = max(error_i over last prediction_error_window chunks)
```

Robust prediction:

```text
robust_prediction_Bps = base_prediction_Bps / (1 + err)
```

Fallback when prediction-error history is unavailable:

```text
robust_prediction_Bps = base_prediction_Bps * startup_safety_factor
```

The sequence score and buffer simulation are identical to `mpc`, using `robust_prediction_Bps`.

## Pseudocode

```text
validate rates
if rates has one entry:
    return rates[0]

update actual throughput history from last_fragment_size / last_download_time when valid
compute base_prediction as in mpc
if no valid base_prediction:
    return startup/min representation

if previous predictions and actual throughputs overlap:
    compute absolute percentage errors
    err = max(last prediction_error_window errors)
    predicted = base_prediction / (1 + err)
else:
    predicted = base_prediction * startup_safety_factor

run the same MPC enumeration with predicted throughput
selected_level = first level of best robust sequence
store predicted throughput for the next decision's error calculation
return rates[selected_level]
```

## Edge Cases

| case | required behavior |
| --- | --- |
| empty ladder | validation failure through shared controller contract |
| one-level ladder | return the only rate |
| no actual throughput history | return startup/min representation |
| no previous predictions | use `startup_safety_factor * base_prediction` |
| actual throughput zero | use epsilon denominator; ignore invalid sample if needed |
| very high recent error | robust prediction decreases strongly but remains positive |
| missing buffer | simulate from `0` seconds |
| missing/non-positive segment duration | startup/min representation |
| horizon too large | reduce horizon within sequence limit or fail config |

## Simplifications Accepted

- Same enumerative structure as `mpc`.
- Harmonic mean base predictor.
- Maximum recent absolute percentage error over up to five chunks.
- Conservative startup fallback.
- Internal provisional objective only.

## Simplifications Prohibited

- No Pensieve implementation.
- No RL training.
- No neural inference.
- No ABR server.
- No future throughput oracle.
- No final QoE/reward definition.
- No benchmark scoring or trace/replay code.

## Telemetry And Logging Expectations

Future code may expose controller-local debug fields such as `robust_mpc_base_prediction_Bps`, `robust_mpc_error_max`, `robust_mpc_prediction_Bps`, and `robust_mpc_best_first_level` after provenance is documented. These are diagnostics only.

## Compatibility With `baseline_entry_contract.md`

- Target rate is bytes per second.
- Representation ladder comes from MPD/client state.
- Quality levels are representation indices.
- Decisions do not depend on console output.
- The controller must not modify runtime code, player code, metrics, configs, output artifacts, or evaluation gates.

## Acceptance Criteria

The future implementation must pass `acceptance_tests.md`, behave like MPC when prediction error is zero, become more conservative when recent error is high, and never instantiate Pensieve or neural/RL components.

## Risks

- Prediction-error accounting must align predictions with the later observed chunk.
- Conservative correction may under-select quality after short transient errors.
- Internal objective weights remain provisional.
- If exact segment sizes are unavailable, RobustMPC inherits MPC's size approximation risk.

## Memory/Thesis Usage

Use this spec in Chapter 5 after MPC. Chapter 2 should position RobustMPC as a strong classical robust baseline and cite Pensieve only as a comparison source. Chapter 6 should compare RobustMPC against MPC after evaluation methodology exists.
