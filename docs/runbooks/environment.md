# Environment Setup And Checks

Phase 1 keeps the default development path pure Python and import-safe on Windows. GStreamer is an optional Linux runtime capability for real playback validation, not a hard dependency for tests or config loading.

## Roles

### Windows Host

- Editing and Codex work.
- Pure Python tests.
- Config/import checks.
- Default fake-engine runner path.
- No required GStreamer playback.

### Ubuntu Client VM

- Real runtime validation.
- Pulls the repository via git.
- Runs fake and GStreamer client modes.
- Runs GStreamer capability checks.

### Ubuntu Server VM

- Hosts MPD files and DASH segments over HTTP.
- Keeps media content outside this repository.

## Validation Tiers

### Tier 1 - Pure Unit Checks

Tier 1 covers importability, config loading, environment profile behavior, and run-context metadata helpers.

- Must pass on Windows without GStreamer.
- Must not require network access, media files, GUI, server infrastructure, ML tooling, or `config/client.local.yaml`.
- Covered by `tests/test_imports.py`, `tests/test_config.py`, `tests/test_environment_check.py`, and `tests/test_run_context.py`.

### Tier 2 - Offline Fake-Engine Smoke Tests

Tier 2 exercises the official config runner path with a synthetic local MPD, fake media engine, patched downloader, and temporary output root.

- Must pass on Windows and Ubuntu.
- Must not require network access, GStreamer, media files, GUI, server infrastructure, ML tooling, or `config/client.local.yaml`.
- Covered by `tests/test_fake_client_smoke.py`.

### Tier 3 - Ubuntu Runtime Checks

Tier 3 uses a real MPD served outside the repository and optional GStreamer on the Ubuntu client VM.

- Manual/operational for now.
- Not unit tests.
- Not benchmark results yet.

## Dependency Types

### Python Runtime Dependencies

Install the minimal runtime path with:

```powershell
pip install -r requirements.txt
```

This installs only Python dependencies needed by imports, config loading, the default non-interactive runner, the fake media engine path, and tests. `requests` is required by the MPD parser and segment downloader.

`PyYAML` is not required. `core/client_config.py` uses it if present, but falls back to the simple YAML subset used by `config/client.example.yaml`.

### Optional Analysis Dependencies

Offline analysis uses `numpy`, `pandas`, and `matplotlib`. Install them only when running `analysis_metrics.py`:

```powershell
pip install -r requirements-analysis.txt
```

### Optional GStreamer Dependencies

GStreamer/PyGObject are Linux/system dependencies. They are intentionally not listed in `requirements.txt` because they are not portable pip dependencies for the Windows/default test path.

On Ubuntu client, install:

```bash
sudo apt update
sudo apt install -y python3-gi gir1.2-gstreamer-1.0 gstreamer1.0-tools \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav
```

GStreamer presence means the environment can attempt real media playback. It does not make the current `gst` path benchmark-grade by itself.

## Windows Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover
python -m py_compile main.py core\client_config.py core\controller\registry.py core\controller\base.py core\controller\contract.py core\controller\fixed_quality.py core\controller\scripted_quality.py core\runtime_feedback.py core\run_context.py core\dataset_schema.py player.py scripts\check_environment.py
python scripts/check_environment.py --profile dev
python scripts/check_environment.py --profile gst
```

Expected result: all commands pass without GStreamer installed.

## Ubuntu Client Setup

From the repository root:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip curl
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover
python -m py_compile main.py core/client_config.py core/controller/registry.py core/controller/base.py core/controller/contract.py core/controller/fixed_quality.py core/controller/scripted_quality.py core/runtime_feedback.py core/run_context.py core/dataset_schema.py player.py scripts/check_environment.py
python scripts/check_environment.py --profile dev
python scripts/check_environment.py --profile gst
python scripts/check_environment.py --profile gst --strict
```

Use `--system-site-packages` so the virtual environment can see Ubuntu's `python3-gi` package.

`python scripts/check_environment.py --profile gst` reports GStreamer status and exits 0 even when optional pieces are missing. Add `--strict` when the Ubuntu client is expected to have full GStreamer capability.

Install the GStreamer Ubuntu packages listed above before expecting the strict GST check to pass.

## Environment Checker Profiles

```bash
python scripts/check_environment.py --profile dev
python scripts/check_environment.py --profile analysis
python scripts/check_environment.py --profile gst
python scripts/check_environment.py --profile all
python scripts/check_environment.py --profile gst --strict
```

- `dev`: required default checks; fails if Python, runtime modules, or core imports are broken.
- `analysis`: optional analysis modules; warns by default, fails with `--strict`.
- `gst`: optional GStreamer/PyGObject/tools; warns by default, fails with `--strict`.
- `all`: runs `dev`, `analysis`, and `gst`; without `--strict`, only required dev failures make the command fail.

## Git Hygiene

Keep local and generated artifacts out of commits:

- `config/client.local.yaml`
- `.venv/`
- `__pycache__/`
- `logs/`
- `analysis_output/`
- local media directories and segment/video files
- generated datasets and zip files

Missing GStreamer must not break import/config tests.
