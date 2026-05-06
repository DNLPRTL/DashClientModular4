# Hardening Step 1: Importability

Date: 2026-05-06

This step makes the current skeleton importable from the tracked repository without adding any new ABR algorithms.

## What Changed

- `main.py` no longer eagerly imports missing controllers such as BOLA, MPC, BBA, PPO, PANDA, or FESTIVE.
- A small controller registry was added at `core/controller/registry.py`.
- The registry exposes only controllers that exist in the repository today: `MaxQualityController`.
- `main.py` now builds its controller menu from that registry.
- `core/media_engine/gst_media_engine.py` can now be imported even when PyGObject or GStreamer is not installed. Instantiating `GstMediaEngine` still requires the real GStreamer runtime.
- A minimal import smoke test was added at `tests/test_imports.py`.

## Why

Phase 1 hardening is about making the base client clean and runnable before adding real ABR comparisons. Missing eager imports made `main.py` fail before the client could even start. The registry keeps the current surface honest: only tracked, available controllers are offered, and future controllers can be added deliberately after the base player contract is stable.

No benchmark logic was changed in this step.
