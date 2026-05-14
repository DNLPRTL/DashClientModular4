# Source evidence â€” rate_based

Phase: 2.2A â€” PDF-grounded source evidence  
Baseline: `rate_based` / throughput-based  
Primary source: Liu, Bouazizi, Gabbouj, "Rate Adaptation for Adaptive HTTP Streaming", MMSys 2011.  
Status: evidence layer only. Not an implementation spec and not runtime code.

## Purpose

This document extracts the implementation-relevant evidence from the primary paper before producing `implementation_spec.md`, `controller_api_mapping.md`, `acceptance_tests.md`, and `notes_for_memory.md`.

The goal is to make the future `rate_based` controller implementable in DashClientModular4 without Codex reading raw PDFs.

## Paper role in the TFG

`rate_based` is the simple classical throughput-based baseline. It is included because it represents the family of ABR controllers that use measured or predicted network capacity to select the next representation.

It is not intended to be the strongest baseline. It is intended to be a transparent lower-complexity comparator against BBA, BOLA, MPC and RobustMPC.

## Evidence extracted from Liu 2011

### Receiver-driven HTTP adaptation

The paper frames adaptive HTTP streaming as a receiver-driven/client-side process. The client sends a sequence of HTTP GET requests for media segments, and before requesting the next segment it can decide which representation to request.

Operational evidence for DashClientModular4:
- Decisions are made at segment boundaries.
- The controller does not need server-side state.
- The controller can use MPD-derived representation bitrates.
- The controller only needs application-layer observations.

### Segment Fetch Time (SFT)

The paper defines Segment Fetch Time as the time from sending the GET request for a segment to receiving the last bit of that segment.

Operational interpretation:
- `last_segment_download_time_s` is the implementation equivalent of SFT.
- If SFT is invalid, zero, missing or not finite, the controller must fall back to a safe representation.

### Media Segment Duration (MSD)

The paper compares SFT with the media duration contained in the segment.

Operational interpretation:
- `segment_duration_s` is the implementation equivalent of MSD.
- Segment duration is required for the paper's original ratio-based interpretation.
- DashClientModular4 may also compute throughput directly from bytes/time; both views must be documented.

### Ratio mu

The paper defines:

```text
mu = MSD / SFT
```

where:
- `MSD` = media segment duration.
- `SFT` = segment fetch time.

Interpretation:
- `mu > 1`: segment downloaded faster than playback duration; network may support current bitrate and possibly a higher bitrate.
- `mu == 1`: current encoded bitrate approximately matches measured average throughput.
- `mu < 1`: segment download is slower than playback; current bitrate is unsafe.

The smoothed throughput can be interpreted as:

```text
estimated_throughput_current_units = mu * current_representation_bitrate
```

Equivalent direct measurement for implementation:

```text
measured_throughput_bps = 8 * last_segment_size_bytes / last_segment_download_time_s
```

The direct measurement is easier in DashClientModular4 if segment size is available. The ratio interpretation remains valuable for explaining the paper.

### Smoothing and segment duration

The paper argues against using instantaneous TCP transmission rate and instead uses segment-level measurements over a longer interval. It notes that segments around 5â€“10 seconds can smooth short-term TCP variations.

Operational decision:
- Do not require TCP instantaneous rate.
- Use segment-level throughput, optionally with EWMA or harmonic mean smoothing.
- If the actual DASH content uses shorter/longer segments, document this as a limitation of direct paper equivalence.

### Step-wise increase and aggressive decrease

The paper proposes conservative upward movement and aggressive downward movement across representation levels.

Operational decision for first implementation:
- Upward movement should be conservative: at most one representation level per stable decision window, unless explicitly configured otherwise.
- Downward movement should be aggressive: if safe throughput is below current representation bitrate or buffer is critically low, select the highest safe lower representation, potentially dropping multiple levels.
- Avoid oscillation by adding hysteresis or a safety factor.

### No TCP-layer requirement

The paper explicitly states that the method does not require RTT or packet loss from the TCP layer.

Operational decision:
- Forbidden signals: TCP RTT, TCP packet loss, congestion window, sender state, server state, external bandwidth oracle.
- Allowed signals: segment size, segment download time, representation bitrate, segment duration, buffer level as safety guard.

## Required signals for DashClientModular4

| Signal | Unit | Role | Status |
|---|---:|---|---|
| representation ladder | representation index + bitrate | candidate actions | required |
| current representation bitrate | bps or B/s after conversion | throughput comparison | required |
| last segment download time | seconds | SFT / throughput denominator | required |
| last segment size | bytes | direct throughput computation | required if available |
| segment duration | seconds | MSD / paper ratio | required |
| measured throughput | bytes/s or bps | safe-rate selection | derivable |
| throughput history | list of rates | smoothing | optional but recommended |
| buffer level | seconds | safety guard only | required for guard |
| current quality level | representation index | step-wise transition | required |
| next segment index | integer | telemetry/context | optional |

## Units and conversions

DashClientModular4 contract uses target rates in bytes per second when `target_rate` is used.

Common conversions:
```text
bitrate_bps = bitrate_kbps * 1000
bitrate_Bps = bitrate_bps / 8
throughput_Bps = last_segment_size_bytes / last_segment_download_time_s
throughput_bps = 8 * throughput_Bps
safe_throughput_Bps = throughput_Bps * safety_factor
```

The future implementation must be explicit about whether it compares in bits/s or bytes/s. To satisfy the existing contract, output `target_rate` should be bytes/s if used.

## Suggested implementation evidence to carry into 2.2B

Initial algorithm should be:

```text
if no valid ladder:
    return no decision or safe fallback according to baseline_entry_contract.md

if no valid throughput measurement:
    select minimum representation or configured startup representation

estimate throughput from last segment or history
apply safety_factor, e.g. 0.85
candidate = highest representation with bitrate <= safe throughput

if buffer_level_s <= critical_buffer_s:
    force minimum or lower safe representation

if candidate > current_level:
    increase by at most one level unless conservative_up=false

if candidate < current_level:
    allow multi-level decrease

return representation index or target rate using DashClientModular4 contract
```

## Simplifications accepted

- EWMA or harmonic mean can be used as a smoothing estimator.
- Direct bytes/time throughput can be used instead of explicitly computing `mu`, as long as the link to Liu 2011 is documented.
- Buffer level can be used as a safety guard even though throughput is the primary decision signal.

## Simplifications prohibited

- Do not require TCP RTT or packet loss.
- Do not require server-side logic.
- Do not define this as a final QoE benchmark.
- Do not claim it is equivalent to all production throughput-based algorithms.
- Do not compare fake-engine smoke results as benchmark results.
- Do not use console output as an input signal.

## Edge cases to preserve for later specs

- Empty representation ladder.
- Single-representation ladder.
- Missing segment size.
- Missing download time.
- Zero or negative download time.
- Throughput estimate below minimum bitrate.
- Throughput estimate above maximum bitrate.
- Critically low buffer.
- Startup with no history.
- Representation bitrates in bps vs target rate in B/s.

## Acceptance-test evidence

Future tests should check:
- chooses minimum when no throughput exists;
- chooses highest safe bitrate below measured throughput;
- does not use RTT/loss fields;
- downshifts aggressively when throughput drops;
- upshifts conservatively;
- applies buffer guard;
- returns units compatible with baseline_entry_contract.md.

## What this paper does not justify

- It does not justify BBA, BOLA, MPC or RobustMPC.
- It does not justify final QoE/reward.
- It does not justify trace/replay benchmark.
- It does not justify neural/RL controllers.
- It does not justify TCP-layer instrumentation.

## Use in memory

Chapter 2:
- Use as the source for classical throughput-based ABR.

Chapter 5:
- Use to explain implementation of the simple rate-based controller.

Chapter 6:
- Use as one classical baseline in later evaluation, once benchmark methodology is defined.

Suggested figure:
- "rate_based controller: segment download measurement -> safe throughput -> representation selection."

Suggested table:
- signal mapping from Liu 2011 to DashClientModular4.