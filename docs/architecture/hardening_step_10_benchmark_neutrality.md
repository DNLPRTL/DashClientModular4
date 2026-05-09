# Hardening Step 10: Benchmark Neutrality Contract

Date: 2026-05-09

This step formalizes benchmark-neutral evaluation metadata without implementing academic ABR baselines, AI, final QoE, final reward, or benchmark scripts.

## What Changed

- Added `core/benchmark_contract.py` with pure helpers for segment phase classification, segment evaluation eligibility, stall classification, and stall evaluation eligibility.
- Added `eval_phase` to `dataset.csv` and `dataset_training.csv`.
- Kept `use_for_eval` as the canonical row-level benchmark eligibility flag and now derives it from the explicit evaluation phase contract.
- Added tests for init, startup, warm-up, steady-state, drain, terminal, error, terminal drain stall, startup stall, invalid values, and deterministic helper behavior.
- Extended the offline fake-engine smoke test to assert `eval_phase` and `use_for_eval` consistency.
- Added `docs/architecture/telemetry_metric_audit.md`.

## Evaluation Phases

The contract uses stable phase names:

- `init`
- `startup`
- `warmup`
- `steady_state`
- `drain`
- `terminal`
- `error`

Only successful steady-state media rows are benchmark-evaluable in this block. Init, startup, warm-up, drain, terminal, and error rows are not benchmark rows. Rows with missing or invalid classification inputs fail safe as non-evaluable.

`fixed_quality` and `scripted_quality` remain deterministic test/debug controllers that provide guardrails for this metadata. They are not academic ABR baselines. `max_quality` remains legacy/debug/stress behavior.

## Stall Classes

The contract defines stable stall/event class names:

- `startup_stall`
- `rebuffer`
- `terminal_drain_stall`
- `runtime_only`
- `unknown`

Terminal drain stalls must not be counted as steady-state rebuffering. Startup stalls are classified separately from rebuffering. Real mid-playback rebuffer events remain evaluable by the pure helper, but event-level stall telemetry is still pending because current CSV rows only contain segment-level stall aggregates.

## No Runtime Semantics Change

This block adds metadata and pure classification helpers only. It does not change playback order, segment downloads, controller choice logic, ABR policy behavior, downloader behavior, parser behavior, media-engine behavior, retry/backoff logic, buffer pacing, drain mechanics, stall generation, throughput estimation, GStreamer timing, or network behavior.

The fake engine remains the controlled path for reproducible tests. GStreamer remains integration/runtime only and is not benchmark-grade.

## Current Caveats

The client is not final benchmark-grade until Phase 1 acceptance.

Final QoE and reward definitions remain pending until paper-driven methodology is selected.

Academic baseline implementation remains pending.

AI or learned-controller design remains pending.

Fake-engine and GStreamer behavior are not claimed to be equal.
