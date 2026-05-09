# Phase 1 Status - Client Hardening

## Goal

Convert DashClientModular4 into an ABR-neutral, reproducible, benchmark-oriented DASH client skeleton before implementing real ABR controllers.

## Completed

### Block 1 - Importability

- Removed eager imports of missing controllers from `main.py`.
- Added controller registry exposing only tracked controllers.
- `GstMediaEngine` module can be imported without local GStreamer/PyGObject.
- Added minimal import smoke tests.
- No new ABR algorithms were implemented.
- Player/benchmark logic was intentionally not changed.

### Block 2 - Config Runner

- Added a non-interactive config-driven runner path in `main.py`.
- Added config loading and validation in `core/client_config.py`.
- Kept manual interactive mode behind `--interactive`.
- Removed hard-coded LAN MPD URLs from the default run path.
- Kept `config/client.local.yaml` ignored by git.
- Added tests for config loading and controller lookup from config.
- No new ABR algorithms were implemented.

### Block 3 - Dependencies And Environment

- Added minimal runtime dependency declaration in `requirements.txt`.
- Added optional analysis dependencies in `requirements-analysis.txt`.
- Added `scripts/check_environment.py` with `dev`, `analysis`, `gst`, and `all` profiles.
- Kept GStreamer/PyGObject optional and outside the Windows/default pip path.
- Added environment checker tests that do not require real GStreamer.
- Kept runner/config/registry imports compatible with Python 3.8.
- Added environment setup runbook and architecture note.
- No benchmark semantics were changed.

### Block 4 - Reproducible Run Layout

- Added `core/run_context.py` to create authoritative run directories.
- Each non-interactive run now writes `run_manifest.json`, `config.resolved.json`, `environment.json`, `run.log`, and the existing dataset CSVs in one `logs/run_*` directory.
- Added run context tests.
- Added run layout runbook and architecture note.
- No benchmark/runtime semantics were changed.

### Block 5 - Minimal Smoke Tests

- Added an offline fake-engine smoke test through the official `main.main(argv)` config runner path.
- The smoke test uses a temporary local MPD, `FakeMediaEngine`, and a patched downloader at `main.SegmentDownloader`.
- The smoke test blocks external HTTP and requires no GStreamer, media files, GUI, server, ML tooling, or `config/client.local.yaml`.
- The test asserts the reproducible run layout writes manifest, resolved config, environment, log, dataset, and training CSV artifacts.
- Documented Phase 1 validation tiers across README, runbooks, and the Block 5 architecture note.
- No ABR algorithms were added and no runtime/benchmark semantics were changed.

### Block 6 - Dataset / Telemetry Schema Contract

- Added `core/dataset_schema.py` with explicit dataset and training header builders.
- Prefixed feedback-derived `dataset.csv` columns with `feedback_` to avoid collisions with top-level row columns such as `segment_index`.
- Kept `dataset.csv` as the full telemetry CSV and `dataset_training.csv` as the minimal training-oriented CSV.
- Added schema unit tests and extended the fake-engine smoke test to assert unique headers and row/header length alignment.
- Units, row values, output filenames, output paths, ABR decisions, buffering, downloader behavior, parser behavior, QoE logic, and GStreamer timing were not changed.
- Current generated datasets remain validation artifacts, not final benchmark results.

### Block 7 - Controller API / ABR Decision Contract

- Added `core/controller/contract.py` with the controller contract version, required feedback keys, feedback units, target-rate unit, feedback-key validation helpers, rate-ladder validation, and shared quantization helper.
- Kept the current dict-based controller API for backward compatibility: `setPlayerFeedback(feedback_dict)`, `calcControlAction()`, `getControlAction()`, `quantizeRate(rate)`, and `getIdleDuration()`.
- Documented that controller target rates are in bytes per second and quality levels are integer indices into the MPD bitrate ladder.
- Updated `BaseController.quantizeRate()` to delegate to the shared quantizer while preserving fallback behavior when feedback or rates are missing.
- Added controller contract tests covering feedback keys, units, rate validation, quantization semantics, `BaseController`, and `MaxQualityController`.
- No new ABR algorithms were added and no runtime/player refactor, benchmark-neutrality work, dataset semantics change, QoE finalization, downloader change, parser change, or GStreamer timing change was introduced.

### Block 8 - Deterministic Test Controllers / Client Invariant Harness

- Added `fixed_quality` and `scripted_quality` as deterministic test/debug controllers.
- Documented that these controllers are not academic ABR baselines; they exist to verify client-path behavior without policy ambiguity.
- Registered `fixed_quality`, `scripted_quality`, and the existing `max_quality` controller.
- Kept `max_quality` available for backward compatibility as legacy/debug/stress behavior, not as a comparable baseline.
- Updated official fake-engine smoke coverage and the example config to prefer `fixed_quality` level `0`.
- Added deterministic controller tests for clamping, feedback `max_level`, missing feedback, scripted segment-index behavior, registry creation, and `max_quality` compatibility.
- No academic, learned, AI, or adaptive ABR controller was added.
- No runtime/player refactor, benchmark-neutrality work, dataset semantics change, QoE finalization, downloader change, parser change, buffering change, retry change, warm-up change, preroll change, pacing change, stall handling change, throughput-estimation change, media-engine behavior change, or GStreamer timing change was introduced.

### Block 9 - Runtime / Player Responsibility Split

- Added `core/runtime_feedback.py` with `build_controller_feedback()` as the first extracted runtime helper.
- Kept `Player.get_feedback()` as the public Player method and delegated it to the helper without changing the feedback payload.
- Preserved the legacy dict-based controller contract, feedback key order, rate units, throughput-estimation semantics, and dataset CSV schema.
- Added unit tests covering feedback key order, measured and fallback bandwidth values, explicit fragment-duration overrides, and the Player wrapper path.
- Reused `fixed_quality` and `scripted_quality` as deterministic guardrails for the runtime/controller split.
- No ABR baseline, AI controller, benchmark-neutrality work, QoE/reward change, downloader change, parser change, buffering change, retry/backoff change, warm-up change, preroll change, pacing change, drain change, stall-semantics change, GStreamer timing change, or media-engine behavior change was introduced.

## Current Constraints

- Do not implement BBA, BOLA, MPC, robustMPC, PPO, PANDA, FESTIVE, SARA, ELASTIC, RBC, WISH, or any real ABR controller yet.
- Keep only deterministic test/debug controllers plus legacy max-quality stress behavior until the base client is stable.
- Prioritize reproducibility, config-driven execution, headless validation, and clean run outputs.

## Pending Technical Direction After Block 9

The next implementation block is not started in this commit. Runtime responsibility separation, benchmark neutrality, baseline ABR algorithms, final QoE metrics, reward definitions, benchmark comparisons, and analysis input/output alignment remain pending technical direction after Block 9.

GStreamer remains an integration/runtime path for now and is not benchmark-grade. Fake-engine and GStreamer behavior are not claimed to be equal.
