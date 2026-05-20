# bola Notes For Memory

## Neutral Academic Summary

The `bola` baseline represents utility-based buffer control. It evaluates each representation with a BOLA-style score that combines buffer occupancy, segment duration, representation utility, and representation size. Unlike rate-based methods, it does not rely on explicit bandwidth prediction.

Implementation status: Phase 2.3.4 implements `bola` as the third academic ABR baseline after `rate_based` and `bba`. The code is BOLA-basic, not dash.js DYNAMIC, FAST SWITCHING, BOLA-E, or production dash.js behavior.

## Citation Plan

Primary citation: Spiteri et al. 2020, `spiteri2020bola`.

Auxiliary practical citation: Spiteri et al. 2019, `spiteri2019dashjs`, only for explaining production caveats and why DYNAMIC, FAST SWITCHING, and BOLA-E are deferred.

## Chapter 2 Contribution

Use BOLA to introduce theoretically grounded buffer-based ABR and Lyapunov/utility-style decision making. It should be contrasted with BBA: both use buffer, but BBA uses a hand-designed buffer map while BOLA uses an optimization-derived score.

BOLA follows BBA in the implementation order because BBA first validates the client as a buffer-driven baseline path. BOLA then keeps buffer as the central signal but replaces the reservoir/cushion map with a utility/size score for each candidate representation.

## Chapter 5 Contribution

Use the implementation spec to describe:

- `queued_time` to `Q_segments` conversion;
- utility calculation;
- segment-size use: optional exact per-level sizes if supplied, otherwise approximation as `rate * segment_duration`;
- configurable/defaulted `bola_v=5.0` and `bola_gamma=0.2`;
- BOLA-basic boundary;
- absence of DYNAMIC and FAST SWITCHING.
- no-download/wait limitation: all non-positive scores fall back to minimum rate because the current controller contract cannot express wait.

## Chapter 6 Contribution Later

After methodology exists, BOLA can be compared with BBA to show the effect of utility-based buffer optimization, and with MPC/RobustMPC to compare buffer-only and prediction-based methods.

## Suggested Table

BOLA variable mapping:

| BOLA concept | DashClientModular4 equivalent |
| --- | --- |
| buffer `Q` | `queued_time / fragment_duration` |
| representation size `S_m` | `rates[m] * fragment_duration` |
| utility `v_m` | `ln(rate_m / min_rate)` |
| candidate action | representation index from `rates` |

## Suggested Figure

Original diagram: buffer level and ladder enter BOLA score calculation; highest-score representation becomes target rate. Add a note box: DYNAMIC and FAST SWITCHING deferred.

## Limitations To Disclose

- BOLA-basic is not production dash.js.
- `V` and `gamma` require careful configuration or later derivation.
- Exact per-segment VBR sizes are not available in the first spec.
- No-download/wait is not expressed in the first controller contract.
- BOLA utility is not final evaluation QoE.

## Test Defense Notes

The unit tests prove the decision rule by checking exact fixture scores, low-buffer fallback, higher-buffer movement to higher levels, exact-size handling, size approximation, invalid input fallback, parameter defaults, and forbidden-signal invariants. They also prove that throughput is not required and that target rates remain bytes/s while quality levels remain representation indices.

## Defense Message

BOLA is included because it is the central utility-based buffer baseline. The implementation is deliberately scoped to a reproducible BOLA-basic variant so that practical dash.js features do not blur the academic comparison. Smoke validation is integration evidence only, not a claim that BOLA is better or worse than BBA, rate-based, MPC or RobustMPC.
