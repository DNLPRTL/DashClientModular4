# Hardening Step 2: Config Runner

Date: 2026-05-06

This step adds a config-driven runner path without adding any ABR algorithms.

## What Changed

- `main.py` now defaults to a non-interactive config runner.
- Manual prompts are available only through `python main.py --interactive`.
- `config/client.example.yaml` now documents the runner schema.
- `config/client.local.yaml` remains ignored by git and is the intended place for local MPD URLs.
- A config loader was added at `core/client_config.py`.
- The loader reads the example config and overlays a selected local config.
- The controller registry is used to instantiate the configured controller.
- The registry now accepts optional controller params, such as `debug: false` for `MaxQualityController`.
- The run config controls:
  - `mpd_url`
  - media engine name: `fake` or `gst`
  - media engine minimum queue time
  - controller name and params
  - initial quality level
  - whether the controller may override the initial quality before startup
  - headless mode
  - output root directory and dataset filename
  - downloader retry count and verbosity
  - player buffer threshold, drain sleep, and preroll window
- The hard-coded LAN MPD URL was removed from the default run path.
- The manual parser helper no longer contains a hard-coded LAN MPD URL.
- No RL model path is used by the default run path.
- A resolved config JSON is written into the player run directory when possible.
- Config loading and controller lookup tests were added.

## Why

Phase 1 hardening needs reproducible runs before adding or comparing ABR controllers. Interactive input, hard-coded MPD URLs, and untracked local choices make benchmark results difficult to repeat. The runner now makes the selected content, engine, controller, headless mode, and basic runtime parameters explicit in config.

The fake engine remains the default because it is import-safe and does not require GStreamer on Windows. Selecting GStreamer is still supported, but it fails only at runtime if the machine does not have the required system dependencies.

## Boundaries Preserved

- No BBA, BOLA, MPC, robustMPC, PPO, PANDA, FESTIVE, SARA, ELASTIC, RBC, WISH, SODA, or other ABR algorithm was implemented.
- `Player` was not deeply refactored.
- Existing player policies are only exposed through config where safe for this step; they are not redesigned here.
- The official config path defaults `initial_controller_decision` to `false` so `initial_quality` is reproducible. The legacy controller-first startup behavior remains available through config.
- The only tracked controller remains `max_quality`.

## Usage

```powershell
Copy-Item config\client.example.yaml config\client.local.yaml
# Edit config\client.local.yaml and set mpd_url.
python main.py --config config\client.local.yaml
```

See `docs/runbooks/run_client.md` for the full runbook.
