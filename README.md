# DashClientModular4

Modular DASH client for a TFG project. Phase 1 is focused on hardening the base client into an ABR-neutral, reproducible benchmarking skeleton before adding real ABR algorithms.

## Current Run Path

The official benchmark/dev path is config-driven and non-interactive:

```powershell
Copy-Item config\client.example.yaml config\client.local.yaml
# Edit config\client.local.yaml and set mpd_url.
python main.py --config config\client.local.yaml
```

`config/client.local.yaml` is ignored by git and must hold local MPD URLs or machine-specific settings. The example config defaults to:

- `media_engine.name: "fake"`
- `controller.name: "max_quality"`
- `playback.initial_controller_decision: false`
- `playback.headless: true`
- `output.root_dir: "logs"`

Manual demo prompts are still available with:

```powershell
python main.py --interactive
```

See [docs/runbooks/run_client.md](docs/runbooks/run_client.md) for exact usage.

Each non-interactive execution writes a self-contained run directory under `logs/` by default:

```text
logs/run_YYYYMMDD_HHMMSS/
```

That directory contains the run manifest, resolved config, environment snapshot, run log, and the existing dataset CSVs. See [docs/runbooks/run_layout.md](docs/runbooks/run_layout.md).

`dataset.csv` is the full telemetry CSV. Feedback-derived columns use a `feedback_` prefix, for example `feedback_segment_index`, so they do not collide with top-level row columns. `dataset_training.csv` remains the minimal training-oriented CSV. These files are still validation artifacts, not final benchmark results.

Controllers still use the legacy dict-based API. Feedback keys and units are documented in `core/controller/contract.py`; target rates are bytes per second, and quality levels are integer indices into the MPD bitrate ladder. This contract is test-protected, but baseline ABR algorithms and benchmark-grade runtime separation are still pending.

## Environment

The supported minimum Python version is 3.8. The default development path does not require GStreamer.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover
python scripts/check_environment.py --profile dev
```

Optional offline analysis dependencies live in `requirements-analysis.txt`. Optional GStreamer support is checked separately on Ubuntu with:

```bash
python scripts/check_environment.py --profile gst
python scripts/check_environment.py --profile gst --strict
```

See [docs/runbooks/environment.md](docs/runbooks/environment.md) for the Windows host, Ubuntu client VM, and Ubuntu server VM setup.

## Test Tiers

Phase 1 validation is split into three tiers:

- Tier 1: pure import, config, environment, and run-context tests. These must pass on Windows without GStreamer.
- Tier 2: offline fake-engine smoke tests. These must pass on Windows and Ubuntu without network, GStreamer, media files, GUI, server, ML tooling, or `config/client.local.yaml`.
- Tier 3: Ubuntu runtime checks with a real MPD and optional GStreamer. These are manual/operational checks for now, not unit tests and not benchmark results.

Run Tier 1 and Tier 2 with:

```powershell
python -m unittest discover
```

## Main Structure

- `core/controller`: controller interface and registry.
- `core/controller/contract.py`: controller feedback, units, target-rate, and quantization contract.
- `core/media_engine`: fake and GStreamer playback engines.
- `core/parser`: MPD parser and DASH parsing helpers.
- `core/downloader.py`: segment downloader.
- `core/run_context.py`: run directory and metadata helper.
- `core/dataset_schema.py`: dataset and training CSV schema helpers.
- `config`: example client configuration.
- `scripts/check_environment.py`: environment capability checks.
- `docs`: architecture notes and runbooks.
- `tests`: import, config, environment, run-context, and offline fake-client smoke tests.

## Important Rule

DASH videos, segments, and other heavy media files must not be committed to this repository. DASH content lives outside the repo and is referenced through local ignored config.
