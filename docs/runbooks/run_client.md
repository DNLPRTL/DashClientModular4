# Run The DASH Client

This is the official Phase 1 benchmark/dev path. It is non-interactive and driven by YAML config.

Before running the client on a fresh machine, follow `docs/runbooks/environment.md` and verify:

```powershell
python scripts/check_environment.py --profile dev
```

## 1. Create Local Config

From the repository root:

```powershell
Copy-Item config\client.example.yaml config\client.local.yaml
```

Edit `config/client.local.yaml` and set at least:

```yaml
mpd_url: "http://your-server/path/video.mpd"
```

`config/client.local.yaml` is ignored by git, so local URLs and machine-specific settings stay out of commits.

## 2. Select The Existing Trivial Controller

For the current hardening phase, use the tracked registry controller:

```yaml
controller:
  name: "max_quality"
  params:
    debug: false
```

Do not select controllers that are not in `core/controller/registry.py`.

## 3. Select The Media Engine

Use the fake engine for benchmark/dev runs and import-safe tests:

```yaml
media_engine:
  name: "fake"
  min_queue_time: 1.0
```

GStreamer can be selected only on machines with GStreamer and PyGObject installed:

```yaml
media_engine:
  name: "gst"
  min_queue_time: 1.0
  decode_video: false
  sink_name: null
```

Missing GStreamer does not break config loading or import tests. It only fails when a run explicitly requests `media_engine.name: "gst"`.

## 4. Keep Benchmark Runs Headless

The benchmark/dev default is:

```yaml
playback:
  initial_quality: 0
  initial_controller_decision: false
  headless: true
```

`initial_controller_decision: false` means the configured initial quality is used for startup. Setting it to `true` restores the legacy behavior where the controller can override the initial level before the first media segment.

Manual GUI mode is not the default. For manual inspection only, either set `headless: false` in local config or run:

```powershell
python main.py --interactive
```

## 5. Run

```powershell
python main.py --config config\client.local.yaml
```

If no `--config` is provided, `main.py` will try `config/client.local.yaml` when it exists. An empty `mpd_url` fails fast with a configuration error instead of prompting.

## 6. Output

The output root is controlled by config:

```yaml
output:
  root_dir: "logs"
  dataset_filename: "dataset.csv"
```

Each non-interactive run creates one timestamped subdirectory under that root:

```text
logs/run_YYYYMMDD_HHMMSS/
```

That directory is the authoritative run artifact. It contains:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `dataset.csv`
- `dataset_training.csv`
- `run.log`

Generated run artifacts are validation output, not benchmark results yet, and must not be committed. See `docs/runbooks/run_layout.md`.

On Ubuntu, inspect the latest runs with:

```bash
find logs -maxdepth 2 -type f | sort
cat logs/run_*/run_manifest.json
```

## 7. Tests

Run import and config tests:

```powershell
python -m unittest discover
python -m py_compile main.py core\client_config.py core\controller\registry.py player.py scripts\check_environment.py
```

Missing GStreamer must not break these default checks. Use `python scripts/check_environment.py --profile gst` on the Ubuntu client VM to inspect GStreamer capability.
