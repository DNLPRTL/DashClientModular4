# rate_based Notes For Memory

## Neutral Academic Summary

The `rate_based` baseline represents classical client-side throughput adaptation. It measures segment download performance at the application layer, smooths the estimate, applies a conservative margin, and selects the highest representation below the safe throughput.

## Citation Plan

Primary citation: Liu et al. 2011, `liu2011rateAdaptation`.

Use Bentaleb et al. 2019 only for taxonomy context if needed. Do not cite TCP-level mechanisms because the selected implementation deliberately avoids RTT and packet-loss inputs.

## Chapter 2 Contribution

Use this baseline to introduce throughput-based ABR as the simplest classical family. Emphasize receiver-driven segment-boundary decisions and application-layer measurements.

## Chapter 5 Contribution

Use the implementation spec to explain:

- feedback keys used by the controller;
- bytes/s target-rate contract;
- throughput calculation from segment size and download time;
- EWMA/conservative estimator;
- safety factor and low-buffer guard.

## Chapter 6 Contribution Later

After evaluation methodology exists, this baseline can act as a transparent lower-complexity comparator against BBA, BOLA, MPC, and RobustMPC. Fake-engine smoke tests should be described as validation, not benchmark results.

## Suggested Table

`rate_based` signal mapping:

| paper concept | DashClientModular4 signal |
| --- | --- |
| SFT | `last_download_time` |
| MSD | `fragment_duration` |
| measured throughput | `last_fragment_size / last_download_time` |
| representation ladder | `rates` |
| safety buffer guard | `queued_time` |

## Suggested Figure

Original diagram: segment download measurement -> throughput smoothing -> safety factor -> highest safe representation -> target rate.

## Limitations To Disclose

- Segment-level throughput is not a network-layer capacity oracle.
- EWMA and safety factor are implementation choices.
- Buffer is only a guard, so the algorithm may react poorly when throughput appears high but buffer is low.
- No final QoE/reward is defined here.
- No GStreamer benchmark claim is made.

## Defense Message

This baseline is intentionally simple and interpretable. It establishes the throughput-driven end of the comparison before buffer-based and MPC-style controllers are introduced.
