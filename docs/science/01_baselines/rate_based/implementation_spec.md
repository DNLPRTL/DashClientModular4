# rate_based Implementation Spec

## Controller Identity

| field | value |
| --- | --- |
| controller name | `rate_based` |
| family | throughput-based / rate-based ABR |
| primary source | Liu et al. 2011, `paper_card.md`, `source_evidence.md` |
| implementation status | implemented in Phase 2.3.2 as the first academic ABR baseline |
| code module | `core/controller/rate_based.py` |
| test module | `tests/test_rate_based_controller.py` |

## Objective

`rate_based` selects the highest representation whose bitrate is below a conservative application-layer throughput estimate. Throughput is the primary signal. Buffer level is only a safety guard and never replaces the throughput rule.

This controller does not define final QoE/reward, trace replay, benchmark methodology, or comparative claims against BBA, BOLA, MPC or RobustMPC.

## Inputs From DashClientModular4

| input | client key | unit | role | status |
| --- | --- | --- | --- | --- |
| representation ladder | `rates` | bytes_per_second_list | candidate representations | required |
| current quality level | `level` | representation_index | conservative upshift and downshift context | required with safe fallback |
| measured throughput | `bwe` or explicit throughput key | bytes_per_second unless key suffix says otherwise | preferred application-layer measurement | allowed |
| last segment size | `last_fragment_size` | bytes | direct throughput numerator | allowed |
| last download time | `last_download_time` | seconds | SFT / throughput denominator | allowed |
| throughput history | `throughput_history*` | bytes_per_second unless key suffix says otherwise | conservative fallback when present | optional |
| buffer level | `queued_time` | seconds | low-buffer safety guard only | allowed |
| segment duration | `fragment_duration` | seconds | paper mapping / documentation context | allowed |
| segment index | `segment_index` | index | reproducibility/debug context | optional |

## Outputs To DashClientModular4

`calcControlAction()` returns `target_rate` in bytes per second. `quality_level` remains the representation index obtained through `quantizeRate(target_rate)`.

The controller does not write CSV files, mutate `eval_phase`, change `use_for_eval`, parse console output, download segments, parse MPDs, or alter metrics.

## Parameters

| parameter | default | unit | implementation note |
| --- | ---: | --- | --- |
| `safety_factor` | `0.85` | ratio | applied to the selected throughput estimate before ladder selection |
| `ewma_alpha` | `0.5` | ratio | smooths segment-level measurements |
| `critical_buffer_s` | `2.0` | seconds | low-buffer guard threshold |
| `startup_level` / `startup_quality` | `0` | representation_index | fallback when no valid throughput or history exists |
| `conservative_upshift` / `conservative_up` | `true` | boolean | limits upward moves |
| `max_upshift_levels` | `1` | levels | default one-level upshift cap |
| `aggressive_downshift` / `allow_multi_level_down` | `true` | boolean | allows multi-level decrease when throughput is unsafe |
| `min_valid_download_time_s` | `0.0` | seconds | zero/negative download times are invalid |

These parameters are configurable through the existing `controller.params` mechanism. No new config schema or runtime plumbing was added.

## Formulas And Units

Direct segment throughput:

```text
throughput_Bps = last_fragment_size_bytes / last_download_time_s
```

Bits to bytes conversion when a feedback key explicitly uses `bps`:

```text
throughput_Bps = throughput_bps / 8
```

EWMA update:

```text
smoothed_Bps = ewma_alpha * throughput_Bps
               + (1 - ewma_alpha) * previous_smoothed_Bps
```

Safe throughput:

```text
safe_throughput_Bps = decision_throughput_Bps * safety_factor
```

Candidate selection:

```text
candidate_level = max(i where rates_Bps[i] <= safe_throughput_Bps)
target_rate_Bps = rates_Bps[candidate_level]
```

The paper ratio `mu = MSD / SFT` remains the explanatory link to Liu et al. 2011. The implementation uses direct bytes/time because DashClientModular4 already exposes segment size and download time.

## Decision Rule

```text
normalize the ladder in bytes/s
if the ladder is missing, empty or malformed:
    return 0.0 as a safe no-ladder fallback

if the ladder has one representation:
    return that representation

prefer a valid measured throughput key when available
otherwise derive throughput from last_fragment_size / last_download_time
otherwise use valid throughput history or existing EWMA state
otherwise return startup_level, default 0

update EWMA when a new measurement exists
if the instantaneous measurement is unsafe for the current level:
    use the lower of instantaneous and EWMA for aggressive downshift

apply safety_factor
select the highest rate <= safe throughput
if queued_time is missing:
    do not upshift
if queued_time <= critical_buffer_s:
    force at least one level lower when possible
if conservative_upshift is true:
    limit upward moves to max_upshift_levels
return rates[chosen_level] in bytes/s
```

## Edge Cases

| case | behavior |
| --- | --- |
| empty or missing ladder | return `0.0` without crashing |
| malformed or non-positive ladder | return `0.0` without crashing |
| one-level ladder | return index `0` |
| no valid throughput and no history | return startup/min representation |
| zero or negative download time | ignore measurement and fall back safely |
| throughput below minimum | choose minimum representation |
| throughput above maximum | choose maximum, subject to conservative upshift |
| low buffer | reduce or hold down the candidate as a safety guard |
| missing current level | use last selected level or startup level |
| explicit `bps` throughput/rate unit | convert to bytes/s before comparison |

## Forbidden Signals

The implementation intentionally does not use TCP RTT, packet loss, congestion window, sender/server state, external bandwidth oracles, console output, GStreamer-only observations, future throughput oracles, final QoE/reward, replay traces, or benchmark results.

## Telemetry And Logging

The controller stores `last_metrics` for local inspection in tests and debugging. These fields are not canonical telemetry columns and do not replace `segment_telemetry.csv`, `evaluation_segments.csv`, the manifest, or the resolved config.

## Validation Status

Phase 2.3.2 validation consists of:

- unit tests in `tests/test_rate_based_controller.py`;
- full `python -m unittest discover`;
- strict client readiness check;
- fake-engine smoke run through the current CLI/config path.

The fake smoke run validates integration and artifact production only. It is not a benchmark and does not prove `rate_based` is better or worse than any later baseline.
