# Code Understanding And Defense Checklist

Use this checklist before the implementation chapter and defense preparation.

## Client Flow

- Explain how `main.py` loads configuration and starts a run.
- Explain how config resolution produces canonical settings.
- Explain how `RunContext` and output artifacts support reproducibility.
- Explain why console output is non-canonical.

## Controller Path

- Explain the controller registry.
- Explain `setPlayerFeedback()`, `calcControlAction()`, `quantizeRate()` and `getIdleDuration()`.
- Explain why target rates are bytes per second.
- Explain why quality levels are representation indices.
- Explain where the representation ladder comes from.
- Explain why controllers must not parse MPDs or download segments.
- Explain why `min_rate`, `fixed_rate`, and `max_rate` were implemented before academic ABR baselines.
- Explain how the registry maps config names to controller classes.

## Media Engine Boundary

- Explain the media engine abstraction.
- Explain fake engine vs GStreamer.
- Explain why fake engine is controlled validation.
- Explain why GStreamer is integration/demo, not benchmark-grade.

## Telemetry And Artifacts

- Explain `run_manifest.json`, `config.resolved.json`, `environment.json`, `run.log`, `segment_telemetry.csv` and `evaluation_segments.csv`.
- Explain why `dataset.csv` and `dataset_training.csv` are legacy/deprecated.
- Explain `eval_phase` and `use_for_eval` as gates, not final scores.
- Explain why terminal drain stalls are not steady-state rebuffering.

## Baseline Formulas

- Explain rate_based throughput calculation and safety factor.
- Explain why `rate_based` is the first academic ABR baseline after sanity controllers.
- Explain that `rate_based` uses application-layer segment size/time or measured download rate, not TCP RTT/loss/cwnd.
- Explain that `rate_based` returns target rates in bytes/s and quality levels are representation indices.
- Explain why `rate_based` uses buffer only as a low-buffer guard.
- Explain BBA reservoir/cushion mapping.
- Explain why `bba` follows `rate_based` as the second academic ABR baseline.
- Explain that BBA is buffer-based, not throughput-based.
- Explain what BBA-0 simplification means and why startup capacity estimation is deferred.
- Explain that `bba` returns target rates in bytes/s and quality levels are representation indices.
- Explain BOLA utility, segment-size approximation and BOLA-basic boundary.
- Explain why BOLA follows BBA in the implementation order.
- Explain how BOLA differs from BBA: utility/size score instead of reservoir/cushion map.
- Explain how `queued_time`, `fragment_duration`, `bola_v`, `bola_gamma`, utility and segment size enter the BOLA score.
- Explain that exact per-level segment sizes are optional and otherwise approximated as `rate * fragment_duration`.
- Explain that all non-positive BOLA scores fall back to minimum rate because no-download/wait is not expressible in the current controller contract.
- Explain why DYNAMIC, FAST SWITCHING and BOLA-E are deferred.
- Explain MPC harmonic mean, horizon enumeration, buffer simulation and internal objective.
- Explain RobustMPC prediction-error correction and why it is not Pensieve.

## Tests And Limitations

- Explain each controller unit test category.
- Explain sanity controller tests for min, fixed, max and target-rate unit conversion.
- Explain fake smoke scenarios and why they are not benchmarks.
- Explain no final QoE/reward in Phase 2.
- Explain no traces/replay/emulation yet.
- Explain no AI/RL implementation yet.
- Explain every simplification honestly.

## Final Defense Check

For every claim in slides or memory, point to one of:

- a source card or evidence document;
- an implementation spec;
- a controller API mapping;
- an acceptance test;
- a readiness or artifact contract;
- a future limitation.
