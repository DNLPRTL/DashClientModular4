# Source evidence â€” BOLA

Phase: 2.2A â€” PDF-grounded source evidence  
Baseline: `bola` / buffer-based utility/Lyapunov  
Primary source: Spiteri, Urgaonkar, Sitaraman, "BOLA: Near-Optimal Bitrate Adaptation for Online Videos", IEEE/ACM ToN 2020.  
Practical source: Spiteri, Sitaraman, Sparacio, "From Theory to Practice: Improving Bitrate Adaptation in the DASH Reference Player", TOMM 2019.  
Status: evidence layer only. Not an implementation spec and not runtime code.

## Purpose

This document extracts implementation-relevant evidence from BOLA before producing the operational Markdown specs.

## Paper role in the TFG

BOLA is the canonical theoretically grounded buffer-based ABR baseline. It differs from BBA because it does not use a simple hand-designed reservoir/cushion map. Instead, it formulates ABR as utility maximization and derives a per-decision rule from Lyapunov optimization.

## Evidence extracted from Spiteri 2020

### Utility maximization

BOLA formulates bitrate adaptation as a utility maximization problem:
- higher bitrate increases utility;
- rebuffering decreases utility;
- utility can be provider/content/device dependent;
- a concave utility such as logarithmic utility is a natural default in examples.

Operational decision:
- First implementation should use a documented utility function.
- Recommended simple utility:
```text
utility_m = log(bitrate_m / bitrate_min)
```
or equivalently normalized monotonic utility.
- Utility must be controller-internal until final QoE/reward is defined later.

### No explicit bandwidth prediction

BOLA's key implementation advantage is that the decision can be made from buffer level and representation properties without explicit bandwidth prediction.

Operational decision:
- Do not use throughput as a primary BOLA input.
- Throughput may only be used later for optional practical safety guards if explicitly documented.
- The first BOLA implementation should be reproducible and deterministic.

### BOLA decision score

The BOLA decision in the paper is based on maximizing, for each representation `m`, a ratio of the form:

```text
score_m = (V * (utility_m + gamma * p) - Q) / S_m
```

where:
- `V` is a control parameter;
- `gamma` controls the relative emphasis on avoiding rebuffering;
- `p` is segment duration in the paper notation;
- `Q` is buffer occupancy in segment units;
- `S_m` is the segment size for representation `m`;
- `utility_m` is the utility of representation `m`.

Operational adaptation:
- DashClientModular4 commonly tracks buffer in seconds.
- Convert to BOLA segment units:
```text
Q_segments = buffer_level_s / segment_duration_s
```
- If exact segment size is unavailable:
```text
S_m_bytes = bitrate_Bps_m * segment_duration_s
```
- Use consistent units for all `S_m`.

### No-download option

The paper's full model includes a no-download/wait option when the buffer is too full.

Operational decision for DashClientModular4:
- The first controller should document the no-download concept but may not be able to express "wait" through the controller API.
- If the controller API cannot express no-download, choose highest valid score and rely on scheduler/player logic for pacing.
- This limitation must be explicit in `implementation_spec.md`.

### Parameter choice

BOLA uses parameters `V` and `gamma`, and later discusses deriving them from intuitive buffer targets:
- `Qmax`: maximum buffer target;
- `Qlow`: low-buffer threshold where the controller should prefer lowest bitrate.

Operational decision:
- Implementation may expose `bola_qmax_s` and `bola_qlow_s` as intuitive configuration parameters.
- It may derive `V` and `gamma` from them, or use documented defaults.
- If derivation is too risky initially, keep `V` and `gamma` configurable and document the limitation.

### Practical production concerns

The ToN paper and the 2019 dash.js paper make clear that production BOLA required practical adaptations:
- smaller buffer capacities;
- startup and seek responsiveness;
- delays unrelated to network conditions;
- possible segment abandonment;
- BOLA-E / DYNAMIC / FAST SWITCHING in dash.js.

Operational decision:
- The initial TFG implementation is BOLA-basic, not full dash.js BOLA-E.
- Use `dashjs_practical_evidence.md` as warning against overclaiming.
- Do not implement DYNAMIC or FAST SWITCHING in the initial BOLA controller.

## Required signals for DashClientModular4

| Signal | Unit | Role | Status |
|---|---:|---|---|
| buffer_level_s | seconds | main BOLA state | required |
| segment_duration_s | seconds | convert buffer to segment units | required |
| representation ladder | index + bitrate | candidate actions | required |
| representation bitrate | bps or B/s | size approximation | required |
| representation segment size | bytes | preferred `S_m` | optional/derivable |
| utility_m | dimensionless | BOLA score | derivable |
| V | dimensionless/control | BOLA score | parameter |
| gamma | inverse seconds or compatible with `p` | BOLA score | parameter |
| Qmax/Qlow | seconds or segments | intuitive parameter derivation | optional |
| throughput | B/s | not primary | not required |

## Suggested implementation evidence to carry into 2.2B

Initial algorithm should be:

```text
if no valid ladder:
    return safe fallback / no decision according to contract

if segment_duration_s <= 0 or buffer is invalid:
    choose minimum representation

Q_segments = buffer_level_s / segment_duration_s

for each representation m:
    utility_m = log(bitrate_m / bitrate_min)  # or normalized monotonic utility
    S_m = segment_size_m if available else bitrate_Bps_m * segment_duration_s
    score_m = (V * (utility_m + gamma * segment_duration_s) - Q_segments) / S_m

choose representation with maximum positive score

if no positive score:
    choose lowest safe representation or document no-download limitation
```

Potential issue:
- The formula must be dimensionally consistent. Future implementation must choose whether it operates in seconds/bytes or segment-units and keep all formulas consistent.

## Simplifications accepted

- BOLA-basic only.
- Logarithmic utility.
- Segment size approximated as bitrate * segment duration.
- No explicit throughput prediction.
- No BOLA-E, DYNAMIC, FAST SWITCHING.

## Simplifications prohibited

- Do not call BOLA a throughput-based algorithm.
- Do not implement DYNAMIC under the name BOLA.
- Do not claim production dash.js equivalence.
- Do not define final QoE/reward from BOLA utility.
- Do not require neural/RL.
- Do not benchmark fake-engine smoke tests.

## Edge cases to preserve for later specs

- Empty ladder.
- Single representation.
- Missing/invalid buffer.
- Missing/invalid segment duration.
- Zero/negative bitrate.
- No exact segment sizes.
- All scores non-positive.
- Buffer above target.
- BOLA parameter invalidity.
- Unit mismatch between bps, B/s and seconds.

## Acceptance-test evidence

Future tests should verify:
- higher buffer tends to allow higher quality;
- low buffer selects low quality;
- score computation is deterministic;
- throughput is not required;
- segment-size approximation works;
- invalid inputs choose safe fallback;
- output units follow baseline_entry_contract.md.

## What this paper does not justify

- It does not justify a final benchmark QoE.
- It does not justify implementing dash.js DYNAMIC.
- It does not justify implementing FAST SWITCHING.
- It does not justify claiming production-level BOLA.
- It does not justify RL/AI.

## Use in memory

Chapter 2:
- Present BOLA as Lyapunov/utility-based buffer controller.

Chapter 5:
- Explain BOLA-basic implementation and its simplifications.

Chapter 6:
- Later compare BOLA against rate_based, BBA, MPC and RobustMPC.

Suggested figure:
- BOLA score/decision threshold diagram drawn from scratch.

Suggested table:
- BOLA variables and DashClientModular4 equivalents.