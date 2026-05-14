# Source evidence â€” RobustMPC

Phase: 2.2A â€” PDF-grounded source evidence  
Baseline: `robust_mpc`  
Primary sources: Yin et al. 2015; Mao, Netravali, Alizadeh, "Neural Adaptive Video Streaming with Pensieve", SIGCOMM 2017.  
Status: evidence layer only. Not an implementation spec and not runtime code.

## Purpose

This document extracts implementation-relevant evidence for RobustMPC before producing operational specs.

## Paper role in the TFG

RobustMPC is the stronger classical hybrid baseline after MPC. It keeps the MPC structure but makes throughput prediction more conservative when recent prediction errors indicate instability.

It is important because later neural/RL ABR papers compare against it, and because it is a realistic "strong classical baseline" before IA/RL.

## Evidence extracted from Yin 2015

### MPC base

RobustMPC uses the same general structure as MPC:
- predict throughput over a short horizon;
- simulate future buffer evolution;
- optimize an internal QoE objective;
- apply only the first decision.

### Robust lower-bound throughput

The paper describes RobustMPC using a conservative throughput lower bound:

```text
C_hat_robust = C_hat / (1 + err)
```

where:
- `C_hat` is obtained using harmonic mean of the past five chunks;
- `err` is the maximum absolute percentage prediction error over the past five chunks.

Operational decision:
- Implement RobustMPC as a wrapper around MPC's throughput predictor.
- Use recent prediction error to reduce predicted throughput.
- Run the same enumeration as MPC with the robust throughput.

### History requirement

RobustMPC requires both:
- previous predicted throughputs;
- actual measured throughputs.

Operational decision:
- If prediction-error history is unavailable, fall back to conservative MPC:
```text
C_hat_robust = safety_factor * harmonic_mean_throughput
```
- Once enough history exists, compute recent absolute percentage errors.

### Typical horizon and history window

Yin 2015 uses a look-ahead horizon of 5 in its experiments and harmonic mean over the past five chunks.

Operational decision:
- Use `throughput_history_window = 5`.
- Use `prediction_error_window = 5`.
- Keep `horizon` configurable; initial Python implementation may use `H = 3` to avoid combinatorial blow-up, with `H = 5` documented as the paper-aligned setting.

## Evidence extracted from Pensieve 2017

Pensieve compares against Buffer-Based, Rate-Based, BOLA, MPC and RobustMPC. It treats RobustMPC as the closest strong non-neural competitor in several evaluations.

Operational decision:
- Include RobustMPC as mandatory baseline.
- Do not implement Pensieve in Phase 2.
- Use Pensieve only as historical neural/RL reference and comparison source.
- Do not train models.
- Do not add an ABR server.
- Do not create AI/RL runtime code.

Pensieve also uses state inputs such as:
- past throughput samples;
- past download times;
- next chunk sizes;
- current buffer;
- chunks remaining;
- last chunk bitrate.

Operational relevance:
- These signals overlap with what MPC/RobustMPC need.
- They help justify that throughput history, buffer level, chunk sizes and last selected bitrate are standard ABR controller inputs.
- They do not justify implementing neural inference.

## Required signals for DashClientModular4

| Signal | Unit | Role | Status |
|---|---:|---|---|
| representation ladder | index + bitrate | candidate actions | required |
| buffer_level_s | seconds | initial simulated buffer | required |
| segment_duration_s | seconds | buffer simulation | required |
| actual throughput history | B/s or bps | base prediction and error | required |
| previous predicted throughput history | B/s or bps | error computation | required if available |
| prediction_error_history | percentage | robust correction | derivable |
| current/last quality level | index | switch penalty | required |
| horizon | chunks | planning depth | parameter |
| segment sizes | bytes | accurate simulation | optional/derivable |
| internal QoE weights | configurable | controller decision only | parameter |

## Robust error computation

Recommended operational form:

```text
base_prediction = harmonic_mean(last N actual throughputs)

for recent i:
    error_i = abs(predicted_i - actual_i) / max(actual_i, epsilon)

err = max(last K error_i)
robust_prediction = base_prediction / (1 + err)
```

Fallback when history is insufficient:
```text
robust_prediction = base_prediction * startup_safety_factor
```

Recommended parameters:
```text
throughput_history_window = 5
prediction_error_window = 5
startup_safety_factor = 0.85
epsilon_throughput = small positive value
```

## Suggested implementation evidence to carry into 2.2B

Initial algorithm should be:

```text
compute base throughput prediction as in MPC

if enough previous predictions and actual throughput measurements:
    compute absolute percentage prediction errors
    err = max(recent errors)
    predicted_throughput = base_prediction / (1 + err)
else:
    predicted_throughput = base_prediction * startup_safety_factor

run same MPC enumeration with predicted_throughput
return first action of best sequence
record prediction for next decision so future errors can be computed
```

## Simplifications accepted

- Same enumerative structure as MPC.
- Harmonic mean base predictor.
- Max recent absolute percentage error.
- Conservative fallback when insufficient history exists.
- Internal QoE objective only.

## Simplifications prohibited

- Do not implement Pensieve.
- Do not train RL.
- Do not add neural inference.
- Do not introduce ABR server.
- Do not use future throughput oracle.
- Do not define final benchmark QoE.
- Do not claim RobustMPC eliminates all rebuffering.

## Edge cases to preserve for later specs

- No throughput history.
- No previous predictions.
- Actual throughput zero.
- Prediction error infinite/undefined.
- Very high recent error.
- Horizon too large.
- Empty ladder.
- Missing buffer.
- Missing segment duration.
- Current quality unavailable.

## Acceptance-test evidence

Future tests should verify:
- with zero recent error, behaves like MPC;
- with high recent error, selects lower bitrate than MPC in same conditions;
- with insufficient history, uses conservative fallback;
- stores prediction needed for next error computation;
- never uses RL/Pensieve model;
- does not create benchmark claims.

## What this source evidence does not justify

- It does not justify IA/RL implementation.
- It does not justify a Pensieve controller.
- It does not justify ABR server architecture.
- It does not justify final QoE/reward.
- It does not justify replacing the initial baseline order.

## Use in memory

Chapter 2:
- Present RobustMPC as robust hybrid baseline.

Chapter 5:
- Explain conservative prediction correction over MPC.

Chapter 6:
- Later compare against MPC to show effect of robustness.

Suggested figure:
- MPC vs RobustMPC throughput prediction: base estimate -> error correction -> robust estimate.

Suggested table:
- prediction error window, base predictor, robust correction.