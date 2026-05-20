# robust_mpc Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `robust_mpc` |
| family | hybrid / robust model predictive control |
| primary sources | Yin et al. 2015, Mao et al. 2017, `paper_card.md`, `source_evidence.md`, `pensieve_source_artifact_card.md` |
| implementation status | implemented in Phase 2.3.6 as the fifth academic ABR baseline |
| code module | `core/controller/robust_mpc.py` |
| test module | `tests/test_robust_mpc_controller.py` |

## Objective

`robust_mpc` implements RobustMPC as MPC with conservative throughput prediction. It keeps the same bounded enumeration, buffer simulation and controller-internal objective as `mpc`, but reduces the predicted throughput with recent prediction error.

This is not Pensieve, not RL, not neural inference, and not final QoE/reward.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| bitrate ladder | `rates` | bytes_per_second_list | candidate actions | yes |
| buffer level | `queued_time` | seconds | initial simulated buffer | yes, safe `0` fallback when invalid |
| segment duration | `fragment_duration` | seconds | buffer simulation and size approximation | yes |
| last segment size | `last_fragment_size` | bytes | actual throughput sample | optional history update |
| last download time | `last_download_time` | seconds | actual throughput sample | optional history update |
| current/last quality | `level` | representation_index | switching penalty reference | optional, clamped |
| explicit actual throughput history | `throughput_history_Bps` or compatible aliases | bytes_per_second_list | base harmonic predictor | optional |
| previous predicted throughput history | `predicted_throughput_history_Bps` or compatible aliases | bytes_per_second_list | prediction-error calculation | optional |
| explicit prediction-error history | `prediction_error_history` or compatible aliases | ratio_list | robust correction | optional |
| exact segment sizes | `segment_sizes_B` or compatible aliases | bytes_list | download-time simulation | optional |
| remaining segments | `remaining_segments` or compatible aliases | chunks | cap horizon near end | optional |

## State Design

The current controller architecture supports persistent controller instances, so the implementation stores:

- recent actual throughput samples in controller-local state;
- the robust prediction used for the next decision;
- recent absolute percentage prediction errors.

When a later actual throughput sample arrives, the controller compares it with the previously stored prediction and appends the resulting error. The history is bounded by `prediction_error_window`.

External prediction-error or prediction/actual histories can also be provided in feedback for deterministic tests. The runtime path does not require new player or media-engine fields.

## Output To DashClientModular4

Return the first representation of the best robust sequence as `target_rate` in bytes per second. The shared quantizer maps it to a representation index.

## Parameters

| parameter | unit | default | behavior |
| --- | --- | --- | --- |
| `horizon` | chunks | `3` | same default as MPC; invalid values fall back to default |
| `throughput_history_window` | chunks | `5` | harmonic mean base predictor window |
| `prediction_error_window` | chunks | `5` | maximum recent error window |
| `startup_safety_factor` | ratio | `0.85` | conservative fallback when prediction errors are unavailable; invalid or >1 values fall back to default |
| `epsilon_throughput_Bps` | bytes_per_second | `0.001` | avoids division by zero in percentage error |
| `quality_reward_mode` | enum | `log_rate_ratio` | same as MPC |
| `rebuffer_penalty` | utility_per_second | `4.3` | internal controller objective only |
| `switch_penalty` | utility_per_utility_delta | `1.0` | internal controller objective only |
| `startup_level` | representation_index | `0` | safe fallback with no valid base prediction |
| `max_enumerated_sequences` | count | `4096` | reduces effective horizon to avoid combinatorial blow-up |
| `min_valid_throughput_Bps` | bytes_per_second | `0.001` | ignores invalid throughput samples |
| `min_segment_duration_s` | seconds | `0.001` | validates duration before simulation |
| `size_mode` | enum | `exact_or_bitrate_duration` | exact per-level sizes when present, otherwise approximation |

## Units

Rates and throughput are normalized to bytes per second internally. Explicit `Bps`/`bytes_per_second` stays bytes/s, `bps` is divided by `8`, `kbps` by `8/1000`, and `Mbps` by `8/1000000`. Exact segment sizes are normalized to bytes; `B` stays bytes and `b` is divided by `8`.

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

## Internal Objective

The internal sequence score is inherited from MPC:

```text
quality(level) = ln(rates[level] / min_rate)

sequence_score =
    sum(quality(level_t))
    - rebuffer_penalty * sum(rebuffer_s_t)
    - switch_penalty * sum(abs(quality(level_t) - quality(previous_level_t)))
```

This is controller decision logic only and is not final evaluation QoE.

## Pseudocode

```text
validate rates
if rates has one entry:
    return rates[0]

validate segment duration
update actual throughput history from last_fragment_size / last_download_time when valid
if a pending previous prediction and a new actual sample align:
    compute absolute percentage prediction error
    append it to bounded prediction-error history

compute base_prediction as in mpc
if no valid base_prediction:
    return startup/min representation

if prediction-error history is available:
    err = max(last prediction_error_window errors)
    robust_prediction = base_prediction / (1 + err)
else:
    robust_prediction = base_prediction * startup_safety_factor

run the same MPC enumeration with robust_prediction
selected_level = first level of best robust sequence
store robust_prediction for the next decision's error calculation
return rates[selected_level]
```

## Edge Cases

| case | implemented behavior |
| --- | --- |
| empty/missing/malformed ladder | safe `0.0` fallback through controller-local validation |
| one-level ladder | return the only rate |
| no actual throughput history | return startup/min representation |
| no previous predictions | use `startup_safety_factor * base_prediction` when base prediction exists |
| actual throughput zero | ignore invalid actual samples for history-pair calculation and avoid division by zero |
| prediction error infinite/undefined | ignore non-finite error values |
| very high recent error | robust prediction decreases strongly but remains positive |
| missing/invalid buffer | simulate from `0` seconds |
| missing/non-positive segment duration | startup/min representation |
| horizon too large | reduce effective horizon within `max_enumerated_sequences` |
| invalid weights or robust params | fall back to documented defaults |
| no exact segment sizes | approximate as `rate * fragment_duration` |

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
- No DYNAMIC or FAST SWITCHING behavior.

## Diagnostics

The controller stores controller-local `last_metrics` for tests and debugging, including base prediction, robust prediction, correction mode, error history, max error, selected sequence, score components, `pensieve_implemented=False`, `rl_or_neural_state_used=False`, and `internal_objective_only=True`. These diagnostics are not canonical telemetry columns and are not benchmark metrics.

## Compatibility With `baseline_entry_contract.md`

- Target rate is bytes per second.
- Representation ladder comes from MPD/client state.
- Quality levels are representation indices.
- Decisions do not depend on console output.
- The controller does not modify runtime code, player code, metrics, configs, output artifacts, or evaluation gates.

## Acceptance Criteria

The implementation must pass `acceptance_tests.md`, behave like MPC when prediction error is zero, become more conservative when recent error is high, and never instantiate Pensieve or neural/RL components.

## Risks

- Prediction-error accounting must align predictions with the later observed chunk.
- Conservative correction may under-select quality after short transient errors.
- Internal objective weights remain provisional.
- If exact segment sizes are unavailable, RobustMPC inherits MPC's size approximation risk.

## Memory/Thesis Usage

Use this spec in Chapter 5 after MPC. Chapter 2 should position RobustMPC as a strong classical robust baseline and cite Pensieve only as a comparison source. Chapter 6 should compare RobustMPC against MPC only after evaluation methodology exists.
