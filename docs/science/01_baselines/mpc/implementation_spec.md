# mpc Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `mpc` |
| family | hybrid / model predictive control |
| primary source | Yin et al. 2015, `paper_card.md`, `source_evidence.md` |
| implementation status | implemented in Phase 2.3.5 as the fourth academic ABR baseline |
| code module | `core/controller/mpc.py` |
| test module | `tests/test_mpc_controller.py` |

## Objective

`mpc` implements a small-horizon enumerative MPC controller. It predicts future throughput from recent segment measurements, enumerates candidate bitrate sequences, simulates buffer evolution, scores each sequence with an internal provisional objective, and returns the first action of the best sequence.

The objective is controller-internal only. It is not the final TFG QoE/reward and must not be used as benchmark scoring.

## Inputs From DashClientModular4

| input | client key | unit | role | required |
| --- | --- | --- | --- | --- |
| bitrate ladder | `rates` | bytes_per_second_list | candidate actions | yes |
| buffer level | `queued_time` | seconds | initial simulated buffer | yes, safe `0` fallback when invalid |
| segment duration | `fragment_duration` | seconds | future buffer increment and size approximation | yes |
| last segment size | `last_fragment_size` | bytes | throughput sample numerator | optional history update |
| last download time | `last_download_time` | seconds | throughput sample denominator | optional history update |
| explicit throughput history | `throughput_history_Bps` or compatible aliases | bytes_per_second_list | predictor input | optional |
| explicit measured throughput | `measured_throughput_Bps` or compatible aliases | bytes_per_second | predictor input | optional |
| current/last quality | `level` | representation_index | switching penalty reference | optional, clamped |
| exact segment sizes | `segment_sizes_B` or compatible aliases | bytes_list | download-time simulation | optional |
| remaining segments | `remaining_segments` or compatible aliases | chunks | cap horizon near end | optional |

## Output To DashClientModular4

Return the first representation of the best sequence as `target_rate` in bytes per second. The shared quantizer maps the target rate to a representation index.

## Parameters

| parameter | unit | default | behavior |
| --- | --- | --- | --- |
| `horizon` | chunks | `3` | default receding-horizon depth; invalid values fall back to default |
| `throughput_history_window` | chunks | `5` | recent positive samples used by harmonic mean |
| `quality_reward_mode` | enum | `log_rate_ratio` | `ln(rate / min_rate)` dimensionless reward |
| `rebuffer_penalty` | utility_per_second | `4.3` | internal cost for simulated rebuffering; negative values fall back to default |
| `switch_penalty` | utility_per_utility_delta | `1.0` | internal cost for quality variation; negative values fall back to default |
| `startup_level` | representation_index | `0` | safe fallback with no valid prediction |
| `max_enumerated_sequences` | count | `4096` | reduces effective horizon to avoid combinatorial blow-up |
| `min_valid_throughput_Bps` | bytes_per_second | `0.001` | avoids invalid prediction |
| `min_segment_duration_s` | seconds | `0.001` | validates duration before simulation |
| `size_mode` | enum | `exact_or_bitrate_duration` | exact per-level sizes when present, otherwise approximation |

## Formulas

Rates and throughput are normalized to bytes per second internally. Explicit `Bps`/`bytes_per_second` stays bytes/s, `bps` is divided by `8`, `kbps` by `8/1000`, and `Mbps` by `8/1000000`. Exact segment sizes are normalized to bytes; `B` stays bytes and `b` is divided by `8`.

Throughput sample from the last completed segment:

```text
throughput_Bps = last_fragment_size_bytes / last_download_time_s
```

Harmonic mean predictor over recent positive samples:

```text
predicted_Bps = n / sum(1 / throughput_Bps_i for i in recent_positive_samples)
```

Segment-size approximation when exact sizes are unavailable:

```text
segment_size_bytes(level) = rates[level] * segment_duration_s
```

Buffer simulation for each candidate action:

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

collect positive throughput samples from explicit history, explicit measured throughput,
and last_fragment_size / last_download_time
if no positive throughput sample exists:
    return rates[startup_level clamped to ladder]

predicted = harmonic_mean(last throughput_history_window positive samples)
if predicted < min_valid_throughput_Bps:
    return rates[startup_level clamped to ladder]

H = configured horizon, capped by remaining_segments when available
while len(rates) ** H > max_enumerated_sequences and H > 1:
    reduce H

best_score = -infinity
best_first_level = startup_level
for each sequence in product(levels, repeat=H):
    simulated_buffer = buffer_level_s
    previous_level = current level
    score = 0
    for level in sequence:
        size = exact_size[level] if present else rates[level] * segment_duration_s
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

| case | implemented behavior |
| --- | --- |
| empty/missing/malformed ladder | safe `0.0` fallback through controller-local validation |
| one-level ladder | return the only rate |
| no throughput history | return startup/min representation |
| zero or negative throughput | ignore sample |
| missing/invalid buffer | simulate from `0` seconds |
| missing/non-positive segment duration | startup/min representation |
| horizon too large | reduce effective horizon within `max_enumerated_sequences` |
| current level invalid | clamp to valid range for switch penalty |
| invalid penalties | negative values fall back to defaults; zero is allowed |
| exact segment sizes missing | approximate as `rate * fragment_duration` |
| unknown buffer capacity | do not cap simulated buffer in first implementation |

## Simplifications Accepted

- Online enumeration instead of FastMPC table compression.
- Horizon `3` by default for tractability.
- Harmonic mean throughput prediction.
- Segment-size approximation from bitrate and duration when exact sizes are absent.
- Internal provisional objective for controller decision only.

## Simplifications Prohibited

- No FastMPC lookup tables in the first implementation.
- No external solvers.
- No crowdsourced or future-throughput oracle.
- No fairness or multi-client behavior.
- No final QoE/reward or benchmark scoring.
- No neural/RL implementation.
- No RobustMPC prediction-error correction in this block.

## Diagnostics

The controller stores controller-local `last_metrics` for tests and debugging, including predicted throughput, effective horizon, sequence count, selected sequence, score components and the `internal_objective_only` flag. These diagnostics are not canonical telemetry columns and are not benchmark metrics.

## Compatibility With `baseline_entry_contract.md`

- Target rate is bytes per second.
- Representation ladder comes from MPD/client state.
- Quality levels are representation indices.
- Controller decisions do not depend on console output.
- The controller does not mutate CSVs, metrics, parser, downloader, media engine, or evaluation gates.

## Acceptance Criteria

The implementation must pass `acceptance_tests.md`, keep the internal objective clearly labeled as provisional, and remain deterministic for identical feedback and controller state.

## Risks

- Horizon enumeration can grow quickly with ladder size, so the controller caps effective horizon.
- Segment-size approximation may differ from VBR content.
- Internal objective weights affect behavior and are not final benchmark QoE.
- Prediction from short histories can be unstable during startup.

## Memory/Thesis Usage

Use this spec in Chapter 5 to describe MPC implementation. Chapter 2 should position MPC as the hybrid baseline combining throughput and buffer. Chapter 6 must not treat the internal score as final QoE.
