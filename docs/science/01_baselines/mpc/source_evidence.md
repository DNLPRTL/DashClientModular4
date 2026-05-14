# Source evidence â€” MPC

Phase: 2.2A â€” PDF-grounded source evidence  
Baseline: `mpc` / model predictive control  
Primary source: Yin, Jindal, Sekar, Sinopoli, "A Control-Theoretic Approach for Dynamic Adaptive Video Streaming over HTTP", SIGCOMM 2015.  
Status: evidence layer only. Not an implementation spec and not runtime code.

## Purpose

This document extracts implementation-relevant evidence from the MPC paper before producing operational specs.

## Paper role in the TFG

MPC is the canonical hybrid ABR baseline. It combines throughput prediction and buffer occupancy over a moving horizon to optimize an internal QoE objective.

## Evidence extracted from Yin 2015

### Why MPC

The paper argues that pure rate-based algorithms discard buffer information and pure buffer-based algorithms discard throughput prediction. MPC is proposed because it can combine both signals and optimize a multi-term objective over a short future horizon.

Operational decision:
- Use both throughput history and buffer level.
- Do not reduce MPC to only rate-based or only buffer-based.
- Keep horizon small for tractability.

### DASH model

The paper models video as chunks/segments, each of length `L` seconds and encoded at discrete bitrates. The client selects a bitrate `R_k` for chunk `k`.

Operational mapping:
- DashClientModular4 representation ladder = available discrete bitrates.
- Each controller decision selects the next representation index or target rate.
- Segment duration is required to simulate future buffer evolution.

### Buffer dynamics

The paper models buffer occupancy as playback time left in the buffer. Downloading a segment consumes wall-clock time and then adds segment duration to the buffer. If download time exceeds current buffer, rebuffering occurs.

Operational simulation for implementation:
```text
download_time_s = segment_size_bytes / predicted_throughput_Bps
rebuffer_s = max(download_time_s - simulated_buffer_s, 0)
simulated_buffer_s = max(simulated_buffer_s - download_time_s, 0) + segment_duration_s
simulated_buffer_s = min(simulated_buffer_s, buffer_capacity_s if known)
```

If exact segment sizes are unavailable:
```text
segment_size_bytes = bitrate_Bps * segment_duration_s
```

### Moving horizon / receding horizon

MPC predicts future throughput for a short horizon, solves the local optimization, applies the first bitrate decision, then repeats at the next chunk.

Operational decision:
- Implement enumerative MPC with small horizon, e.g. `H = 3` initially.
- `H = 5` is historically common in the paper's experiments, but `H = 3` may be safer for Python implementation if the ladder is large.
- The spec should make `horizon` configurable.

### Throughput prediction

The paper uses harmonic mean of the past five chunks in its experiments for RB/FastMPC.

Operational decision:
- Use harmonic mean of recent throughput samples as the default predictor.
- Ignore non-positive throughput samples.
- If not enough history exists, use current measured throughput or a safe startup fallback.

### Internal QoE objective

The paper optimizes a multi-term QoE objective. The operational version should use an internal objective of the form:

```text
score = quality_reward
        - rebuffer_penalty * rebuffer_s
        - switch_penalty * abs(quality_current - quality_previous)
```

Important:
- This objective is controller-internal.
- It is not the final TFG evaluation QoE/reward.
- The final benchmark reward remains deferred.

### FastMPC is not initial MPC

The paper develops FastMPC as a table-enumeration/compression approach for low overhead. This is not the initial TFG implementation.

Operational decision:
- Implement simple online enumeration first.
- Do not precompute FastMPC lookup tables.
- Do not use external solvers.
- Do not claim exact equivalence to FastMPC.

## Required signals for DashClientModular4

| Signal | Unit | Role | Status |
|---|---:|---|---|
| representation ladder | index + bitrate | candidate actions | required |
| buffer_level_s | seconds | initial simulated state | required |
| segment_duration_s | seconds | future buffer increments | required |
| throughput history | B/s or bps | prediction | required |
| last throughput | B/s or bps | fallback prediction | required |
| current/last quality level | representation index | switch penalty | required |
| horizon | chunks | search depth | parameter |
| segment size matrix | bytes | accurate download simulation | optional |
| remaining segments | integer | cap horizon near video end | optional |
| QoE weights | configurable | internal score only | parameter |

## Suggested implementation evidence to carry into 2.2B

Initial algorithm should be:

```text
if no valid ladder:
    return safe fallback / no decision

if no valid throughput:
    choose minimum or configured startup representation

predicted_throughput = harmonic_mean(last N positive throughput samples)

H = min(configured_horizon, remaining_segments if known)
candidate_sequences = product(ladder_indices, repeat=H)

best_score = -infinity
best_first_action = min_representation

for seq in candidate_sequences:
    simulated_buffer = buffer_level_s
    previous_quality = current_quality
    total_score = 0

    for quality in seq:
        size_bytes = known_size_or_bitrate_times_duration(quality)
        download_time = size_bytes / predicted_throughput
        rebuffer = max(download_time - simulated_buffer, 0)
        simulated_buffer = max(simulated_buffer - download_time, 0) + segment_duration_s

        total_score += quality_reward(quality)
        total_score -= rebuffer_penalty * rebuffer
        total_score -= switch_penalty * abs(quality_reward(quality) - quality_reward(previous_quality))
        previous_quality = quality

    if total_score > best_score:
        best_score = total_score
        best_first_action = seq[0]

return best_first_action
```

## Parameter guidance

Suggested initial defaults for documentation:
```text
horizon = 3
throughput_history_window = 5
rebuffer_penalty = 4.3
switch_penalty = 1.0
quality_reward = normalized bitrate or kbps-scaled bitrate
```

These are controller-internal placeholders and must be reviewed before implementation. They must not be used as final evaluation QoE.

## Simplifications accepted

- Small-horizon enumeration.
- Harmonic mean predictor.
- Segment size approximation from bitrate and duration.
- Internal QoE objective.
- No table compression.

## Simplifications prohibited

- Do not implement FastMPC lookup tables initially.
- Do not use external solvers.
- Do not claim final QoE benchmark.
- Do not implement crowdsourced prediction.
- Do not model fairness or multi-client interaction.
- Do not require future throughput oracle.

## Edge cases to preserve for later specs

- Empty ladder.
- Single representation.
- No throughput history.
- Zero/negative throughput.
- Missing buffer.
- Missing segment duration.
- Horizon larger than remaining segments.
- Large ladder causing combinatorial explosion.
- Missing current quality for switch penalty.
- Buffer capacity unknown.

## Acceptance-test evidence

Future tests should verify:
- chooses higher bitrate when throughput and buffer are high;
- chooses lower bitrate when predicted download would rebuffer;
- penalizes avoidable switching;
- uses first action of best sequence;
- handles missing history safely;
- does not use final QoE claims.

## What this paper does not justify

- It does not justify implementing final benchmark reward now.
- It does not justify FastMPC as first implementation.
- It does not justify server-side ABR.
- It does not justify multi-player fairness.
- It does not justify neural/RL.

## Use in memory

Chapter 2:
- Present MPC as hybrid ABR combining throughput and buffer.

Chapter 5:
- Explain implementation as small-horizon enumerative MPC.

Chapter 6:
- Later compare MPC against simpler and robust baselines.

Suggested figure:
- receding horizon diagram: predict -> enumerate -> simulate buffer -> pick first action.

Suggested table:
- MPC parameters and their role.