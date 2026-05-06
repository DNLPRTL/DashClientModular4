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

## Main Structure

- `core/controller`: controller interface and registry.
- `core/media_engine`: fake and GStreamer playback engines.
- `core/parser`: MPD parser and DASH parsing helpers.
- `core/downloader.py`: segment downloader.
- `config`: example client configuration.
- `docs`: architecture notes and runbooks.
- `tests`: import and config tests.

## Important Rule

DASH videos, segments, and other heavy media files must not be committed to this repository. DASH content lives outside the repo and is referenced through local ignored config.
