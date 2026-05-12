# Phase 1 Status - Client Hardening

## Goal

Convert DashClientModular4 into an ABR-neutral, reproducible, benchmark-oriented DASH client skeleton before implementing real ABR controllers.

## Completed

Current canonical run CSVs are `segment_telemetry.csv` and `evaluation_segments.csv`. Legacy names `dataset.csv` and `dataset_training.csv` are deprecated and are not produced by new default runs.

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
- Each non-interactive run writes `run_manifest.json`, `config.resolved.json`, `environment.json`, `run.log`, and run CSV artifacts in one `logs/run_*` directory.
- Added run context tests.
- Added run layout runbook and architecture note.
- No benchmark/runtime semantics were changed.

### Block 5 - Minimal Smoke Tests

- Added an offline fake-engine smoke test through the official `main.main(argv)` config runner path.
- The smoke test uses a temporary local MPD, `FakeMediaEngine`, and a patched downloader at `main.SegmentDownloader`.
- The smoke test blocks external HTTP and requires no GStreamer, media files, GUI, server, ML tooling, or `config/client.local.yaml`.
- The test asserts the reproducible run layout writes manifest, resolved config, environment, log, and CSV artifacts.
- Documented Phase 1 validation tiers across README, runbooks, and the Block 5 architecture note.
- No ABR algorithms were added and no runtime/benchmark semantics were changed.

### Block 6 - CSV Telemetry Schema Contract

- Added `core/dataset_schema.py` with explicit CSV header builders.
- Prefixed feedback-derived full telemetry columns with `feedback_` to avoid collisions with top-level row columns such as `segment_index`.
- Historical output names from this block were later deprecated by Block 11 in favor of `segment_telemetry.csv` and `evaluation_segments.csv`.
- Added schema unit tests and extended the fake-engine smoke test to assert unique headers and row/header length alignment.
- Units, row values, output filenames, output paths, ABR decisions, buffering, downloader behavior, parser behavior, QoE logic, and GStreamer timing were not changed.
- Current generated CSVs remain validation artifacts, not final benchmark results.

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

### Block 10 - Benchmark Neutrality Contract

- Added `core/benchmark_contract.py` with pure helpers for evaluation phase classification, stall/event classification, and benchmark eligibility flags.
- Added `eval_phase` to both run CSV outputs.
- Kept `use_for_eval` as the canonical row-level benchmark eligibility flag; rows marked `use_for_eval=false` are not benchmark rows.
- Documented that init, startup, warm-up, drain, terminal, and error rows are separate from steady-state rows.
- Documented that terminal drain stalls must not be counted as steady-state rebuffering.
- Added `docs/architecture/telemetry_metric_audit.md` to classify current metrics as `eval_ready`, `runtime_only`, `legacy_debug`, `pending_semantics`, or `deprecated_later`.
- Added benchmark contract tests and extended smoke/schema/import coverage for the new metadata.
- No ABR baseline, AI controller, final QoE/reward definition, downloader change, parser change, media-engine change, retry/backoff change, buffering change, pacing/drain change, GStreamer timing change, or network behavior change was introduced.

### Block 11 - Academic Output Hygiene / Legacy Cleanup

- Added `core/output_artifacts.py` with canonical run artifact filenames and manifest output keys.
- Renamed new run CSV outputs to `segment_telemetry.csv` and `evaluation_segments.csv`.
- Deprecated `dataset.csv` and `dataset_training.csv`; new default runs do not produce them.
- Updated `run_manifest.json` output keys to `run_manifest`, `resolved_config`, `environment`, `segment_telemetry`, `evaluation_segments`, and `run_log`.
- Added manifest benchmark-neutrality metadata documenting that run outputs are not final benchmark results, `use_for_eval` is the row gate, terminal drain stalls are not steady-state rebuffering, final QoE/reward is undefined, and no final IA training dataset exists yet.
- Updated config, schema helpers, tests, README, runbooks, and output artifact documentation around the canonical names.
- No playback semantics, ABR logic, downloader behavior, parser behavior, media-engine behavior, buffering, pacing, drain mechanics, QoE/reward finalization, baselines, AI, Mahimahi, trace infrastructure, benchmark scripts, or GStreamer hardening were introduced.

### Block 12 - GStreamer Integration Hardening / Optional Visible Playback

- Hardened `core/media_engine/gst_media_engine.py` as an integration/demo path.
- Improved unavailable GStreamer/PyGObject diagnostics with explicit guidance for `media_engine.name: fake`, Windows expectations, and Ubuntu `scripts/check_environment.py --profile gst --strict`.
- Added clear missing-element errors for required GStreamer elements and the selected sink.
- Prevented silent fallback to `fakesink` when `media_engine.sink_name` is explicit and cannot be created.
- Added concise startup diagnostics for `decode_video`, selected sink, visible playback, and `min_queue_time`.
- Made GStreamer stop/cleanup safer during repeated calls and partial startup failure.
- Added mocked unit tests for GStreamer integration contracts without requiring real GStreamer, a display server, network, or a DASH server.
- Added `docs/runbooks/gstreamer_playback.md`.
- No ABR baseline, AI, QoE/reward finalization, benchmark methodology change, fake-engine behavior change, downloader change, parser change, controller decision change, runtime feedback change, or CSV semantics change was introduced.

### Block 13 - Phase 1 Acceptance / Semantic Provenance / GUI Roadmap

- Added `docs/architecture/phase1_acceptance.md` to record Windows/Ubuntu acceptance checks, fake-engine criteria, GStreamer criteria, and explicit non-goals.
- Added `docs/architecture/telemetry_column_provenance.md` to document current `segment_telemetry.csv` and `evaluation_segments.csv` columns by source, unit, timing, semantic status, benchmark usability, and risk.
- Added `docs/architecture/runtime_console_output_contract.md` to classify console/progress output as human diagnostics, not benchmark output.
- Registered the future GUI/operator dashboard block in `docs/roadmap/gui_frontend_dashboard.md`.
- Renamed the current progress-window `BW (bwe)` label to a human-readable measured-download-rate label without changing values, timing, playback behavior, or controller decisions.
- Reaffirmed that GStreamer is integration/demo only, visible playback is not academic benchmark validity, and headless `fakesink` validation can complete faster than real time.
- No ABR baseline, AI controller, PPO/training, QoE/reward finalization, trace infrastructure, benchmark scripts, GUI implementation, downloader change, parser change, fake-engine change, GStreamer pipeline change, or playback semantics change was introduced.

### Block 14 - Client Readiness Certification / Baseline-Entry Gate

- Added `docs/architecture/client_architecture_audit.md`, `docs/architecture/baseline_entry_contract.md`, `docs/architecture/metric_catalog.md`, `docs/architecture/client_readiness_report.md`, and `docs/architecture/hardening_step_14_client_readiness.md`.
- Added `scripts/check_client_readiness.py` as an objective static/readiness gate.
- Added canonical current feedback-key metadata through `CURRENT_FEEDBACK_KEYS`, feedback aliases, semantic status, and a default segment telemetry header builder.
- Made `progress_bar.py` import-safe when Tkinter is unavailable; visible UI still requires Tkinter at runtime.
- Added tests for readiness, baseline-entry docs/contracts, and controlled fake-path fragment flow.
- Phase 1 client hardening is ready to close as a stable technical base for Phase 0 methodology and later baseline implementation.
- No baseline algorithm, AI controller, PPO/training, QoE/reward finalization, trace infrastructure, final benchmark script, GUI implementation, fake-engine behavior change, GStreamer pipeline change, or playback semantic change was introduced.

## Current Constraints

- Do not implement BBA, BOLA, MPC, robustMPC, PPO, PANDA, FESTIVE, SARA, ELASTIC, RBC, WISH, or any real ABR controller yet.
- Keep only deterministic test/debug controllers plus legacy max-quality stress behavior until the base client is stable.
- Prioritize reproducibility, config-driven execution, headless validation, and clean run outputs.

## Pending Technical Direction After Block 14

Phase 1 hardening is closed only as a client-readiness milestone. Final methodology is not closed. Event-level stall telemetry, baseline ABR algorithms, final QoE metrics, reward definitions, benchmark comparisons, trace/replay infrastructure, and analysis input/output alignment remain pending technical direction after Block 14.

GStreamer remains an integration/runtime path for now and is not benchmark-grade. Fake-engine and GStreamer behavior are not claimed to be equal.

The recommended next step is to return to Phase 0 methodology work before implementing academic baselines.
