# Run The DASH Client

This is the official Phase 1 validation/dev path. It is non-interactive and driven by YAML config. After Block 14 passes, this client path is considered ready as a stable technical base, while Phase 0 methodology still gates any academic baseline implementation.

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

## 2. Select A Deterministic Test Controller

For official smoke and invariant checks in the current hardening phase, prefer `fixed_quality`:

```yaml
controller:
  name: "fixed_quality"
  params:
    level: 0
```

`fixed_quality` always selects the configured ladder level, after clamping to the available ladder and feedback `max_level`.

`scripted_quality` is also available for deterministic switching traces:

```yaml
controller:
  name: "scripted_quality"
  params:
    levels: [0, 1, 0]
    repeat_last: true
```

`fixed_quality` and `scripted_quality` are test/debug controllers. They are not academic ABR baselines; they exist to verify controller construction, feedback handoff, quantization, switching traces, run outputs, and CSV consistency without policy ambiguity.

`max_quality` remains available for backward compatibility and legacy/debug/stress runs:

```yaml
controller:
  name: "max_quality"
  params:
    debug: false
```

Do not treat `max_quality` as a comparable baseline.

Do not select controllers that are not in `core/controller/registry.py`.

The controller API is still the legacy dict-based contract:

- `setPlayerFeedback(feedback_dict)` receives player feedback.
- `calcControlAction()` returns a target rate in bytes per second.
- `quantizeRate(rate)` maps that target rate to an integer quality level in the MPD bitrate ladder.

Feedback keys and units are documented in `core/controller/contract.py`. Evaluation phases and row eligibility are documented in `core/benchmark_contract.py`. These contracts are prerequisites for future comparable baselines; they are not baseline implementations. Final QoE/reward, academic baselines, and AI design remain pending.

For the baseline-entry contract, see `docs/architecture/baseline_entry_contract.md`.

## 3. Select The Media Engine

Use the fake engine for deterministic dev runs and import-safe tests:

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

With `decode_video: false` and `sink_name: null`, the GST engine selects `fakesink` for headless validation. Optional visible playback uses `decode_video: true` and an explicit or default video sink such as `autovideosink`:

```yaml
media_engine:
  name: "gst"
  min_queue_time: 1.0
  decode_video: true
  sink_name: "autovideosink"
```

Missing GStreamer does not break config loading or import tests. It only fails when a run explicitly requests `media_engine.name: "gst"`. Explicit missing sinks fail clearly instead of silently falling back to `fakesink`. GStreamer is integration/demo only for now and is not benchmark-grade; fake-engine and GStreamer behavior are not claimed to be equal. Headless `decode_video=false`/`fakesink` validation is structural only and may complete faster than real time. See `docs/runbooks/gstreamer_playback.md`.

## 4. Keep Validation Runs Headless

The validation/dev default is:

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
  segment_telemetry_filename: "segment_telemetry.csv"
  evaluation_segments_filename: "evaluation_segments.csv"
```

Each non-interactive run creates one timestamped subdirectory under that root:

```text
logs/run_YYYYMMDD_HHMMSS/
```

That directory is the authoritative run artifact. It contains:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `segment_telemetry.csv`
- `evaluation_segments.csv`
- `run.log`

Generated run artifacts are validation/control output, not final benchmark results yet, and must not be committed. `segment_telemetry.csv` is full runtime telemetry. `evaluation_segments.csv` is compact evaluation-oriented segment data, not a final IA training dataset. In CSV outputs, `eval_phase` separates startup, warm-up, steady-state, drain, terminal, and error context; rows with `use_for_eval=false` are not benchmark rows. Terminal drain stalls must not be interpreted as steady-state rebuffering. Column provenance is documented in `docs/architecture/telemetry_column_provenance.md`. Console/progress output is human diagnostics and must not be parsed by benchmark scripts; see `docs/architecture/runtime_console_output_contract.md`. See `docs/runbooks/run_layout.md`.

On Ubuntu, inspect the latest runs with:

```bash
find logs -maxdepth 2 -type f | sort
cat logs/run_*/run_manifest.json
```

## 7. Validation And Test Tiers

Run Tier 1 and Tier 2 tests:

```powershell
python -m unittest discover
python -m py_compile main.py core\client_config.py core\controller\registry.py core\controller\base.py core\controller\contract.py core\controller\fixed_quality.py core\controller\scripted_quality.py core\run_context.py core\runtime_feedback.py core\dataset_schema.py core\benchmark_contract.py core\output_artifacts.py core\media_engine\base.py core\media_engine\fake.py core\media_engine\gst_media_engine.py player.py scripts\check_environment.py
python scripts\check_environment.py --profile dev
python scripts\check_environment.py --profile gst
python scripts\check_client_readiness.py --strict
```

Tier 1 covers pure import, config, environment, and run-context tests. It must pass on Windows without GStreamer.

Tier 2 covers offline fake-engine smoke tests through the official config runner path. It must pass on Windows and Ubuntu without network, GStreamer, media files, GUI, server infrastructure, ML tooling, or `config/client.local.yaml`.

Tier 3 is manual/operational Ubuntu runtime validation with a real MPD and optional GStreamer. It is not part of `unittest` discovery and is not a benchmark result yet.
