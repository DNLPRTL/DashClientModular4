# Hardening Step 4: Reproducible Run Layout

Date: 2026-05-07

This step makes every non-interactive client execution create a self-contained run directory with metadata and outputs.

## What Changed

- Added `core/run_context.py`.
- `main.py` now creates a run context before playback.
- Each run writes:
  - `run_manifest.json`
  - `config.resolved.json`
  - `environment.json`
  - `run.log`
  - the existing dataset CSV
  - the existing training CSV
- `Player` can now receive a pre-created `run_dir` so it writes the existing CSVs into the authoritative run directory instead of creating another timestamped directory.
- Run-specific logging now writes to `run.log` inside the run directory.
- Added unit tests for the run context helper.

## Why

Benchmark hardening needs runs that can be inspected after the fact. The manifest, resolved config, and environment snapshot make local validation runs auditable without introducing a database, experiment tracker, or ML tooling.

The run directory is now the container for the run. `logs/` remains the default output root, but individual `logs/run_*` directories hold the authoritative artifacts.

## Metadata Captured

`run_manifest.json` includes:

- schema version;
- run id;
- local and UTC creation times;
- output root and run directory;
- config source;
- command-line args;
- Python executable and version;
- platform details;
- working directory;
- git commit, branch, and dirty flag when available;
- controller name and params;
- media engine config;
- headless flag;
- MPD URL;
- relative output paths.

`environment.json` includes:

- Python executable and version;
- platform details;
- working directory;
- runtime package versions such as `requests`;
- optional analysis module availability;
- optional GStreamer/PyGObject/tool availability;
- git metadata.

## Boundaries Preserved

- No ABR algorithms were added.
- No controllers were added.
- The controller API was not redesigned.
- Playback, buffering, retry, warm-up, preroll, pacing, downshift, stall, throughput, QoE, logging schema, and dataset semantics were not changed.
- GStreamer remains optional for Windows/default tests.
- Generated run artifacts remain ignored by git.

## Current Caveat

The datasets produced by this layout are still validation artifacts, not benchmark results. Later hardening blocks still need to address benchmark neutrality, dataset semantics, and analysis inputs.
