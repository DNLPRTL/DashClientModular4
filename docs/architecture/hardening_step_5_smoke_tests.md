# Hardening Step 5: Minimal Smoke Tests

Date: 2026-05-07

This step adds focused offline smoke coverage around the already-hardened client skeleton.

## What Changed

- Added `tests/test_fake_client_smoke.py`.
- The smoke test calls the official non-interactive runner through `main.main(["--config", ...])`.
- The test creates a temporary local DASH MPD with one video `AdaptationSet`, one `Representation`, one init segment, and two media segments.
- The test uses:
  - `media_engine.name: "fake"`
  - `controller.name: "max_quality"`
  - a temporary output root
  - a patched fake downloader at `main.SegmentDownloader`
- External HTTP is blocked by patching `requests.sessions.Session.request`.
- Logging handlers are closed before temporary directory cleanup.

## Validation Tiers

### Tier 1 - Pure Unit Checks

Tier 1 covers pure import, config, environment, and run-context tests.

- Must pass on Windows without GStreamer.
- Must not require network access, media files, GUI, server infrastructure, ML tooling, or `config/client.local.yaml`.
- Current files:
  - `tests/test_imports.py`
  - `tests/test_config.py`
  - `tests/test_environment_check.py`
  - `tests/test_run_context.py`

### Tier 2 - Offline Fake-Engine Smoke Tests

Tier 2 exercises the official runner path with fake runtime dependencies.

- Must pass on Windows and Ubuntu.
- Must not require network access, GStreamer, media files, GUI, server infrastructure, ML tooling, or `config/client.local.yaml`.
- Current file:
  - `tests/test_fake_client_smoke.py`

The Block 5 smoke test asserts that:

- the runner returns exit code 0;
- exactly one `run_*` directory is created under the temporary output root;
- `run_manifest.json`, `config.resolved.json`, `environment.json`, `run.log`, `dataset.csv`, and `dataset_training.csv` exist;
- the manifest status is `completed`;
- the manifest records `max_quality`, fake media engine, headless mode, and canonical dataset outputs;
- the resolved config contains the temporary MPD path;
- both dataset CSVs contain header and data rows;
- the fake downloader sees `init.m4s`, `seg1.m4s`, and `seg2.m4s`;
- no external HTTP request is made.

### Tier 3 - Ubuntu Runtime Checks

Tier 3 covers real runtime validation with a real MPD served outside the repository and optional GStreamer on the Ubuntu client VM.

- Manual/operational for now.
- Not unit tests.
- Not benchmark results yet.

## Boundaries Preserved

- No ABR algorithms were added.
- The controller API was not redesigned.
- `Player` was not deeply refactored.
- Buffering, retry behavior, warm-up, preroll, pacing, downshift behavior, stall handling, throughput estimation, CSV semantics, QoE, GStreamer timing, and benchmark logic were not changed.
- GStreamer remains optional and is not required on Windows.
- The tests do not require a real DASH server or external network.
- The tests do not rely on `config/client.local.yaml`.
- The tests write only inside temporary directories.
