# Source evidence â€” BBA

Phase: 2.2A â€” PDF-grounded source evidence  
Baseline: `bba` / buffer-based  
Primary source: Huang, Johari, McKeown, Trunnell, Watson, "A Buffer-Based Approach to Rate Adaptation", SIGCOMM 2014.  
Status: evidence layer only. Not an implementation spec and not runtime code.

## Purpose

This document extracts implementation-relevant evidence from the BBA paper before producing the operational Markdown specs.

## Paper role in the TFG

BBA is the canonical buffer-based baseline. It is included because it demonstrates the opposite design philosophy from `rate_based`: choose bitrate mainly from buffer occupancy rather than a throughput forecast.

## Evidence extracted from Huang 2014

### Core motivation

The paper argues that future capacity is difficult to estimate in real commercial streaming, and proposes beginning with only the playback buffer as the primary control signal. It asks when capacity estimation is actually needed.

Operational decision:
- The first DashClientModular4 BBA implementation should be buffer-driven, not throughput-driven.
- Throughput can be documented as useful for startup but must not become the main BBA-0 decision signal.

### Buffer as state variable

The paper treats playback buffer occupancy as the state variable the ABR algorithm is trying to control. It argues that the buffer can encode past capacity history once playback has reached steady state.

Operational decision:
- Main input is `buffer_level_s`.
- Representation choice is a deterministic function of buffer level and bitrate ladder.
- The algorithm should be simple enough to test with fake-engine scenarios.

### Startup vs steady state

The paper separates:
- startup phase: buffer is still empty/growing, so crude capacity estimation may help;
- steady-state phase: buffer occupancy can be sufficient for bitrate selection.

Operational decision for first implementation:
- Implement simple BBA-0 style mapping first.
- Document startup throughput guard as optional, not required for first controller.
- Do not overfit Netflix production behavior.

### Reservoir and cushion

BBA defines a reservoir near low buffer levels and a cushion over which bitrate rises from minimum to maximum. The BBA-0 rate map uses:
- `reservoir`: below this, choose minimum bitrate;
- `cushion`: interval after reservoir over which quality increases;
- upper region: after reservoir+cushion, choose maximum bitrate.

Operational adaptation:
```text
if buffer_level_s <= reservoir_s:
    choose min representation
elif buffer_level_s >= reservoir_s + cushion_s:
    choose max representation
else:
    map normalized position within cushion to representation ladder
```

The mapping can be linear or threshold-based. It must be deterministic and documented.

### Discrete representation ladder

The paper's rate map is continuous, but video rates are discrete. It describes switching when the mapped rate crosses barriers to adjacent discrete rates.

Operational decision:
- DashClientModular4 has a discrete ladder.
- Future implementation should choose a representation index.
- A threshold mapping is easier to test than continuous target rate output.
- If target rate is emitted, it must be bytes/s per contract.

### Safety area

The paper reasons about ensuring a chunk can complete before the buffer falls into the reservoir, especially because clients may not cancel an ongoing chunk download.

Operational adaptation:
- Initial BBA-0 can be simple, but acceptance tests should include low-buffer behavior.
- If buffer is invalid or below reservoir, choose minimum.
- Do not claim the simplified implementation reproduces all production safety constraints.

## Required signals for DashClientModular4

| Signal | Unit | Role | Status |
|---|---:|---|---|
| buffer_level_s | seconds | primary decision state | required |
| representation ladder | index + bitrate | candidate actions | required |
| min representation | index | fallback / low buffer | derivable |
| max representation | index | high buffer | derivable |
| reservoir_s | seconds | low-buffer threshold | parameter |
| cushion_s | seconds | ramp interval | parameter |
| current representation | index | optional stickiness | optional |
| measured throughput | bytes/s or bps | optional startup guard | optional only |
| segment_duration_s | seconds | safety reasoning | optional in BBA-0 |

## Parameter guidance

Suggested initial defaults for documentation, to be confirmed in implementation:
```text
reservoir_s = 5.0
cushion_s = 10.0
```

These match the values used for BB in the MPC paper's comparative setup and are suitable for a small, testable implementation. They are not Netflix production values and must not be presented as such.

Alternative:
- make both parameters configurable;
- require `cushion_s > 0`;
- require `reservoir_s >= 0`.

## Suggested implementation evidence to carry into 2.2B

Initial algorithm should be:

```text
if ladder is empty:
    return safe fallback / no decision according to contract

if buffer_level_s is missing, negative or not finite:
    choose minimum representation

if buffer_level_s <= reservoir_s:
    choose minimum representation

if buffer_level_s >= reservoir_s + cushion_s:
    choose maximum representation

x = (buffer_level_s - reservoir_s) / cushion_s
x = clamp(x, 0, 1)
target_index = floor(x * (num_representations - 1))
choose representation at target_index
```

Optional stickiness:
```text
only switch if mapped index crosses a discrete threshold
```

## Simplifications accepted

- BBA-0 style rate map.
- Linear or threshold mapping.
- No startup capacity estimator in first implementation.
- No VBR-specific production tuning.
- No server-side behavior.

## Simplifications prohibited

- Do not use throughput as the main decision rule.
- Do not implement Netflix production internals.
- Do not claim BBA-0 is the full Netflix deployment.
- Do not define final QoE/reward.
- Do not benchmark fake smoke results.
- Do not depend on console output.

## Edge cases to preserve for later specs

- Empty ladder.
- Single representation.
- Missing buffer.
- Negative buffer.
- `cushion_s <= 0`.
- Buffer exactly equal to reservoir.
- Buffer exactly equal to reservoir + cushion.
- Large buffer above max threshold.
- Startup with zero buffer.

## Acceptance-test evidence

Future tests should verify:
- buffer below reservoir -> min representation;
- buffer above reservoir+cushion -> max representation;
- intermediate buffer -> deterministic intermediate representation;
- missing buffer -> safe min;
- no throughput required for standard BBA-0 decision;
- no runtime code touched in documentation blocks.

## What this paper does not justify

- It does not justify a throughput-based controller as the main BBA algorithm.
- It does not justify BOLA's Lyapunov score.
- It does not justify MPC planning.
- It does not justify final QoE/reward.
- It does not justify mobile/Netflix production claims for the TFG implementation.

## Use in memory

Chapter 2:
- Present as classical buffer-based ABR.

Chapter 5:
- Explain the implemented BBA-0-style map.

Chapter 6:
- Later compare against throughput-based, BOLA, MPC and RobustMPC.

Suggested figure:
- reservoir/cushion/rate-map diagram drawn by us, not copied from the paper.

Suggested table:
- buffer thresholds and expected selected quality.