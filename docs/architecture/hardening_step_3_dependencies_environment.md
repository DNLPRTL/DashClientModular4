# Hardening Step 3: Dependencies And Environment

Date: 2026-05-07

This step makes the project environment explicit and checkable without changing playback or benchmark behavior.

## What Changed

- `requirements.txt` now declares the minimal Python dependency for the default config/fake-engine runtime path: `requests`.
- `requirements-analysis.txt` now declares optional offline analysis dependencies: `numpy`, `pandas`, and `matplotlib`.
- `scripts/check_environment.py` was added with profiles for:
  - `dev`
  - `analysis`
  - `gst`
  - `all`
- The environment checker is import-safe on Windows and does not import GStreamer at module import time.
- GStreamer checks are optional by default and become required only with `--strict`.
- Tests were added for the environment checker without requiring real GStreamer.
- Runner/config/registry annotations were kept compatible with Python 3.8.
- `.gitignore` now also excludes common local media and run-output artifacts.

## Why

The project is developed from Windows but validated for real runtime on an Ubuntu client VM. The default development path must stay lightweight and reproducible, while GStreamer support remains a separate environment capability.

Separating dependencies prevents Windows import/config tests from depending on Linux system packages and avoids pulling in analysis or ML stacks for normal client execution.

## Dependency Boundaries

### Required Default Runtime

- Python 3.8 or newer.
- `requests`.
- Project modules required by the config/fake-engine path.

### Optional Analysis

- `numpy`.
- `pandas`.
- `matplotlib`.

These are used by `analysis_metrics.py` only.

### Optional GStreamer

GStreamer/PyGObject are installed through Ubuntu packages, not through `requirements.txt`. Missing GStreamer must not break:

- config loading,
- import smoke tests,
- default fake-engine runner checks,
- Windows development tests.

## Environment Checker Semantics

`python scripts/check_environment.py --profile dev` fails only for required default environment problems.

`python scripts/check_environment.py --profile analysis` reports optional analysis dependencies and exits 0 unless `--strict` is used.

`python scripts/check_environment.py --profile gst` reports PyGObject, `Gst`, `Gst.init(None)`, `gst-launch-1.0`, and `gst-inspect-1.0`. It exits 0 by default and exits non-zero with `--strict` when capability is missing.

`python scripts/check_environment.py --profile all` runs all checks. Without `--strict`, only required dev failures make the command fail.

## Boundaries Preserved

- No ABR algorithms were added.
- No controllers were added.
- `Player` was not refactored.
- Playback, buffering, retry, warm-up, preroll, stall, logging, and dataset semantics were not changed.
- GStreamer was not made a hard dependency for Windows/default tests.
