# Phase 1 Status — Client Hardening

## Goal

Convert DashClientModular4 into an ABR-neutral, reproducible, benchmark-ready DASH client skeleton before implementing real ABR controllers.

## Completed

### Block 1 — Importability

- Removed eager imports of missing controllers from main.py.
- Added controller registry exposing only tracked controllers.
- GstMediaEngine module can be imported without local GStreamer/PyGObject.
- Added minimal import smoke tests.
- No new ABR algorithms were implemented.
- Player/benchmark logic was intentionally not changed.

## Current Constraints

- Do not implement BBA, BOLA, MPC, robustMPC, PPO, PANDA, FESTIVE, SARA, ELASTIC, RBC, WISH, or any real ABR controller yet.
- Keep only trivial/fixed/max controllers needed for smoke tests.
- Prioritize reproducibility, config-driven execution, headless benchmark mode, and clean run outputs.

## Next Block

Block 2 — Add config-driven runner path.

The client should be runnable from a YAML config instead of interactive input or hardcoded paths.