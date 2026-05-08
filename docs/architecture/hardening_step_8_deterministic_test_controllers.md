# Hardening Step 8: Deterministic Test Controllers

Date: 2026-05-08

This step adds deterministic controller fixtures for validating the client path without introducing academic ABR baselines.

## What Changed

- Added `FixedQualityController` as `fixed_quality`.
- Added `ScriptedQualityController` as `scripted_quality`.
- Registered both controllers alongside the existing `max_quality` controller.
- Moved the official fake-engine smoke test to `fixed_quality` so the smoke path does not depend on the legacy max-quality stress behavior.
- Updated the example config to use `fixed_quality` level `0`.

## Controller Purpose

`fixed_quality` and `scripted_quality` are deterministic test/debug controllers. They are not academic ABR baselines and must not be reported as BBA, BOLA, MPC, robustMPC, PPO, PANDA, FESTIVE, SARA, ELASTIC, RBC, WISH, SODA, or any learned/AI policy.

Their purpose is to verify the base client path with policy ambiguity removed:

- controller construction through the registry;
- feedback handoff through the existing `BaseController` API;
- rate-ladder clamping and player-side quantization traces;
- deterministic switching traces from `segment_index`;
- run manifest and output generation;
- dataset and training CSV consistency.

Both controllers set idle duration to `0.0` and select exact rates from `feedback["rates"]`. They do not adapt to throughput, buffer occupancy, stalls, QoE, or downloader timing.

## Existing Max-Quality Controller

`max_quality` remains available for backward compatibility and for legacy/debug/stress runs. It is not a comparable ABR baseline. Official smoke and invariant coverage should prefer `fixed_quality` unless a test specifically needs max-quality behavior.

## Boundaries Preserved

- No academic, learned, AI, or adaptive ABR controller was implemented.
- Player/runtime responsibilities were not refactored.
- Downloader, parser, buffering, retry, warm-up, preroll, pacing, stall handling, throughput estimation, CSV semantics, QoE, GStreamer timing, benchmark logic, and media-engine behavior were not changed.
- Windows tests still do not require GStreamer.
- Tests remain offline and `unittest`-based.

## Current Caveats

Real baseline ABR implementation is still pending.

Runtime/player responsibility separation is still pending.

Benchmark neutrality is still pending.

QoE and reward definitions are not finalized.

GStreamer remains an integration/runtime path for now and is not benchmark-grade.

Fake-engine and GStreamer behavior are not claimed to be equal.
