# Run Layout

Every non-interactive client execution creates one self-contained run directory under the configured output root.

Default shape:

```text
logs/
  run_YYYYMMDD_HHMMSS/
    run_manifest.json
    config.resolved.json
    environment.json
    dataset.csv
    dataset_training.csv
    run.log
```

The run directory is the authoritative artifact for a validation run. Generated run artifacts are local output and must not be committed.

## Files

- `run_manifest.json`: top-level run index with run id, timestamps, command-line args, config source, platform/Python/git metadata, controller, media engine, MPD URL, and relative output paths.
- `config.resolved.json`: resolved config after defaults and local overrides were applied. It may contain local MPD URLs.
- `environment.json`: Python/platform/package/tool availability snapshot.
- `dataset.csv`: existing player dataset output. Schema and semantics are unchanged in Block 4.
- `dataset_training.csv`: existing training CSV output. Schema and semantics are unchanged in Block 4.
- `run.log`: run-specific Python log file. Console output still appears normally.

## Inspect A Run

Windows:

```powershell
python -m unittest discover
python -m py_compile main.py core\client_config.py core\controller\registry.py player.py scripts\check_environment.py
python scripts/check_environment.py --profile dev
```

Ubuntu client:

```bash
git pull --ff-only
source .venv/bin/activate
python -m unittest discover
python scripts/check_environment.py --profile dev
python scripts/check_environment.py --profile gst --strict
python main.py --config config/client.local.yaml
find logs -maxdepth 2 -type f | sort
cat logs/run_*/run_manifest.json
```

For a single run directory:

```bash
RUN_DIR=$(find logs -maxdepth 1 -type d -name 'run_*' | sort | tail -n 1)
cat "$RUN_DIR/run_manifest.json"
cat "$RUN_DIR/environment.json"
head -n 5 "$RUN_DIR/dataset.csv"
```

## Role Split

- Windows host: editing, Codex, pure Python tests, config/import/environment checks. No GStreamer required.
- Ubuntu client VM: real runtime, fake and GStreamer execution, GStreamer capability checks.
- Ubuntu server VM: hosts MPDs and DASH segments over HTTP.

GStreamer availability is an environment capability. It is not proof that the current `gst` path is benchmark-ready.

## Current Status Of Outputs

Current datasets and logs are validation artifacts only. They are useful for inspecting whether the client ran and what it recorded, but they are not benchmark results until later Phase 1 work tightens benchmark neutrality and dataset semantics.

## Git Hygiene

Do not commit:

- `logs/`
- `analysis_output/`
- `config/client.local.yaml`
- media files or DASH segments
- generated datasets
- virtual environments
- machine-specific files
