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
- `dataset.csv`: full telemetry CSV. Feedback-derived columns are prefixed with `feedback_` to avoid collisions with top-level row columns such as `segment_index`.
- `dataset_training.csv`: minimal training-oriented CSV. Its filename and output path are unchanged.
- `run.log`: run-specific Python log file. Console output still appears normally.

## Dataset Schema Contract

Block 6 makes the CSV headers explicit and test-protected:

- `dataset.csv` and `dataset_training.csv` must have unique column names.
- Every data row must have the same number of columns as its header.
- Top-level `segment_index` remains unchanged.
- Feedback-derived columns use the `feedback_` prefix, for example `feedback_segment_index` and `feedback_queued_time`.
- `eval_phase` separates `init`, `startup`, `warmup`, `steady_state`, `drain`, `terminal`, and `error` rows.
- `use_for_eval=false` means the row is not a benchmark row.
- Terminal drain stalls must not be counted as steady-state rebuffering.
- Units and row values from earlier schema blocks remain stable except for explicit evaluation metadata added in Block 10.

The generated CSVs are still validation artifacts, not final benchmark results. The fake engine is the controlled path for reproducible tests. GStreamer runtime validation is still not benchmark-grade yet, and baseline ABR algorithms remain pending.

## Inspect A Run

Windows:

```powershell
python -m unittest discover
python -m py_compile main.py core\client_config.py core\controller\registry.py core\controller\base.py core\controller\contract.py core\controller\fixed_quality.py core\controller\scripted_quality.py core\runtime_feedback.py core\benchmark_contract.py core\run_context.py core\dataset_schema.py player.py scripts\check_environment.py
python scripts/check_environment.py --profile dev
python scripts/check_environment.py --profile gst
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

## Test Tier Coverage

- Tier 1 checks importability, config, environment profiles, and run-context helpers. It must pass on Windows without GStreamer.
- Tier 2 checks this run layout through an offline fake-engine smoke run with a temporary local MPD and patched downloader. It must pass on Windows and Ubuntu without network, GStreamer, media files, GUI, server infrastructure, ML tooling, or `config/client.local.yaml`.
- Tier 3 uses a real MPD and optional GStreamer on Ubuntu as a manual/operational runtime check. It is not a unit test and is not a benchmark result yet.

## Current Status Of Outputs

Current datasets and logs are validation artifacts only. They are useful for inspecting whether the client ran and what it recorded, but they are not final benchmark results until Phase 1 acceptance, final QoE/reward methodology, and baseline controller implementation are complete.

## Git Hygiene

Do not commit:

- `logs/`
- `analysis_output/`
- `config/client.local.yaml`
- media files or DASH segments
- generated datasets
- virtual environments
- machine-specific files
