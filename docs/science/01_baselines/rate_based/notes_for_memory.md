# rate_based Notes For Memory

## Neutral Academic Summary

`rate_based` is the first academic ABR baseline implemented after the sanity controllers. It represents classical client-side throughput adaptation: measure application-layer segment download throughput, smooth it, apply a safety margin, and select the highest representation below the safe estimate.

Primary citation: Liu et al. 2011, `liu2011rateAdaptation`.

## Why It Comes After Sanity Controllers

The sanity controllers (`min_rate`, `fixed_rate`, `max_rate`) were implemented first to prove that the registry, controller contract, target-rate units, representation-index quantization, fake-engine path, and canonical artifacts work before adding an academic algorithm.

`rate_based` then becomes the first scientifically traceable baseline because its paper card, source evidence, implementation spec, API mapping, acceptance tests, and memory notes already exist.

## How Throughput Is Computed

The direct implementation formula is:

```text
throughput_Bps = last_fragment_size_bytes / last_download_time_s
```

If feedback already contains a measured throughput signal such as `bwe` or an explicit `measured_throughput*` key, the controller may use it first. If a key explicitly says `bps` or `kbps`, the controller converts it to bytes/s before comparing with the ladder.

The paper's ratio:

```text
mu = MSD / SFT
```

is the conceptual bridge: downloading a segment faster than its media duration indicates that the current representation may be sustainable. DashClientModular4 uses bytes/time directly because the downloader and player already expose segment size and download time.

## How The Safety Factor Works

The default `safety_factor` is `0.85`.

```text
safe_throughput_Bps = decision_throughput_Bps * 0.85
```

The controller selects the highest ladder rate whose bytes/s value is less than or equal to this safe throughput. This avoids selecting a representation that exactly equals a noisy measured throughput estimate.

## Why RTT And Loss Are Not Required

Liu et al. 2011 supports a receiver-driven HTTP adaptation approach that can operate from segment fetch measurements. The implementation intentionally does not use TCP RTT, packet loss, congestion window, sender/server state, external bandwidth oracles, console output, or future throughput hints.

This makes the baseline compatible with the current DashClientModular4 controller contract and avoids adding network-layer instrumentation.

## Paper-To-Code Mapping

| paper concept | DashClientModular4 implementation |
| --- | --- |
| Segment Fetch Time (SFT) | `last_download_time` |
| media segment duration (MSD) | `fragment_duration` for explanation/context |
| segment-level measurement | `last_fragment_size / last_download_time` |
| available representations | `rates` in bytes/s |
| conservative selection | `safety_factor` |
| smoothed estimate | controller EWMA state |
| conservative increase | `max_upshift_levels=1` by default |
| aggressive decrease | instantaneous unsafe drops may select multiple levels lower |
| buffer safety | `queued_time <= critical_buffer_s` lowers/holds the candidate |

## Fake Smoke Interpretation

Fake smoke validates that:

- `rate_based` can be selected by config;
- it receives controller feedback;
- it returns bytes/s target rates;
- the player quantizes those targets to representation indices;
- canonical artifacts are produced;
- deprecated `dataset.csv` and `dataset_training.csv` are not produced.

Fake smoke does not prove final performance, QoE improvement, real-network superiority, or paper-level benchmark behavior. Comparison against BBA, BOLA, MPC and RobustMPC is deferred until those controllers and the benchmark methodology exist.

## How Tests Prove Correctness

The unit tests prove the local decision rule:

- valid throughput maps to the highest safe representation;
- missing or invalid throughput falls back safely;
- bytes/s and explicit bps conversions are correct;
- low buffer only guards the decision;
- upshifts are conservative;
- downshifts can be multi-level;
- single and invalid ladders are handled safely;
- forbidden RTT/loss/server/oracle fields do not affect decisions.

They do not prove final QoE or benchmark superiority.

## Suggested Chapter Usage

Chapter 2: introduce throughput-based ABR as a classical family.

Chapter 5: explain the implementation with the formulas, contract units, and tests above.

Chapter 6 later: use it as a transparent comparator only after benchmark methodology and final QoE/reward are defined.
