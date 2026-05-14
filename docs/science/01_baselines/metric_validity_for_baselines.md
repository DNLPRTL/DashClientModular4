# Metric Validity For Baselines

This document classifies what controller implementation metrics can mean before final benchmark methodology exists.

## Existing Readiness Constraints

| constraint | current value |
| --- | --- |
| outputs are benchmark results | `false` |
| final QoE/reward defined | `false` |
| final training dataset defined | `false` |
| row evaluation gate exists | `eval_phase` and `use_for_eval` |
| row gate is final benchmark authority | `false` |
| terminal drain stall is rebuffering | `false` |
| fake engine role | controlled implementation validation |
| GStreamer role | integration/demo, not benchmark-grade |

## Metric Classes

| class | examples | valid use now | invalid use now |
| --- | --- | --- | --- |
| Implementation sanity metrics | target rate, chosen level, controller decision path, formula intermediate values | Check a controller follows its spec. | Claim QoE improvement. |
| Integration smoke metrics | run completion, artifact presence, no deprecated output names, readiness pass | Check client integration stayed healthy. | Compare controllers academically. |
| Future benchmark metrics | final QoE, rebuffer score, switching penalty, quality score, trace replay results | Reserved for later methodology. | Use in Phase 2.3 smoke claims. |
| Forbidden or premature claims | "A beats B", "paper-level performance", "real network superiority", "training dataset quality" | None. | Any Phase 2.3 claim. |

## What We Can Say Now

- The controller selected contract-compatible target rates.
- Quantized levels stayed within the representation ladder.
- Telemetry columns were produced.
- Canonical artifacts were produced.
- No forbidden signals were required.
- The smoke scenario completed.
- Readiness checks still passed.

## What We Cannot Say Yet

- Algorithm A is better than algorithm B.
- Final QoE improved.
- Paper-level benchmark performance was reproduced.
- Results generalize to real networks.
- GStreamer playback is benchmark-grade.
- A training dataset is valid.
- A final reward or QoE formula is established.

## Metric-Specific Notes

| metric/signal | current status | decision |
| --- | --- | --- |
| `policy_target_rate` | controller action trace | valid for sanity/integration, not final score |
| `policy_chosen_level` | quantized decision trace | valid for sanity/integration, not final score |
| `feedback_queued_time` | candidate buffer signal | valid controller input where mapped, not fake/GStreamer equivalent benchmark |
| `feedback_last_fragment_size` | download measurement | valid throughput input where mapped, retry semantics still methodological |
| `feedback_last_download_time` | download timing | valid throughput input where mapped, timing semantics still methodological |
| `stall_flag` and `stall_duration` | pending methodology | do not use as final QoE |
| `eval_phase` and `use_for_eval` | neutral row gates | useful later, not final benchmark authority |

## Rule For Future Text

In Phase 2.3 reports, use words like "passes", "selects", "produces", "uses", and "remains compatible". Avoid words like "outperforms", "improves QoE", "generalizes", "benchmark result", or "training quality" unless a later phase explicitly defines that methodology.
