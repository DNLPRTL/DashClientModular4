# Hardening Step 9: Runtime / Player Responsibility Split

Date: 2026-05-09

This step starts separating runtime responsibilities from `Player` without changing runtime semantics.

## What Changed

- Added `core/runtime_feedback.py`.
- Moved legacy controller feedback dictionary assembly into `build_controller_feedback()`.
- Kept `Player.get_feedback()` as the public Player method and delegated it to the extracted helper.
- Added focused unit tests for feedback key order, measured/fallback bandwidth estimation, fragment-duration selection, and the Player wrapper.

## No-Semantics-Change Boundary

This is a structural hardening refactor only. It does not change:

- controller APIs or registered controllers;
- downloader behavior;
- parser behavior;
- buffering semantics;
- retry or backoff behavior;
- warm-up, preroll, pacing, drain, or stall semantics;
- throughput estimation semantics;
- dataset CSV schema or column meanings;
- QoE or reward logic;
- GStreamer timing behavior;
- benchmark logic.

The feedback payload still uses the legacy dict-based controller contract and preserves the existing key order so dataset headers and controller observations stay stable.

## Responsibility Direction

`Player` still owns the current runtime loop, media-engine coordination, CSV writing, stall bookkeeping, warm-up behavior, and drain behavior. This block extracts only one small, testable runtime helper so future hardening can continue in controlled steps.

Controllers and runtime remain separate. Controllers receive feedback and return target rates through the existing contract; they do not own parser, downloader, buffering, retry, stall accounting, CSV schema, GStreamer timing, or benchmark orchestration.

`fixed_quality` and `scripted_quality` provide deterministic guardrails for this split because they remove policy ambiguity while exercising controller construction, feedback handoff, quantization, output generation, and CSV consistency.

## Current Caveats

Benchmark neutrality is still pending.

Final QoE and reward definitions are still pending.

Academic ABR baselines are still pending.

AI or learned-controller design is still pending.

GStreamer remains an integration/runtime path for now and is not benchmark-grade.

Fake-engine and GStreamer behavior are not claimed to be equal.
