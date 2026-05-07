# Phase 1 Status - Client Hardening

## Goal

Convert DashClientModular4 into an ABR-neutral, reproducible, benchmark-ready DASH client skeleton before implementing real ABR controllers.

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

## Current Constraints

- Do not implement BBA, BOLA, MPC, robustMPC, PPO, PANDA, FESTIVE, SARA, ELASTIC, RBC, WISH, or any real ABR controller yet.
- Keep only trivial/fixed/max controllers needed for smoke tests.
- Prioritize reproducibility, config-driven execution, headless benchmark mode, and clean run outputs.

## Next Block

Block 4 - Output layout and reproducibility metadata.

The client should make run directories, manifests, environment metadata, and analysis inputs explicit.
