# Phase 1 Acceptance

Date: 2026-05-11

This document records the acceptance state for Phase 1 client hardening. Block 14 adds the final baseline-entry readiness gate. After that gate passes, Phase 1 client hardening is closed only as a stable technical base for Phase 0 methodology and later ABR baseline implementation. It is not a benchmark methodology and it does not define final QoE, reward, AI training, or academic comparison rules.

## Expected Commit

The required base before this acceptance block is:

- `6f36888` - `Harden GStreamer integration path`

The Block 13 acceptance commit must be a direct descendant of that base. If a future branch moves past it, acceptance must name the exact descendant commit and preserve this provenance.

## Closed Blocks

1. Importability hardening.
2. Config-driven runner.
3. Dependencies and environment checks.
4. Reproducible run layout.
5. Minimal fake-engine smoke tests.
6. Dataset/telemetry schema contract.
7. Controller API / ABR decision contract.
8. Deterministic test controllers.
9. Runtime/player responsibility split.
10. Benchmark neutrality contract.
11. Academic output hygiene / legacy cleanup.
12. GStreamer integration hardening / optional visible playback.
13. Phase 1 acceptance, semantic provenance audit, console contract, and GUI roadmap registration.
14. Client readiness certification / baseline-entry gate.

## Windows Acceptance Checklist

Run from the repository root on Windows:

```powershell
git status --short --branch
git rev-parse --short HEAD
python -m unittest discover
python -m py_compile main.py core\client_config.py core\controller\registry.py core\controller\base.py core\controller\contract.py core\controller\fixed_quality.py core\controller\scripted_quality.py core\run_context.py core\runtime_feedback.py core\dataset_schema.py core\benchmark_contract.py core\output_artifacts.py core\media_engine\base.py core\media_engine\fake.py core\media_engine\gst_media_engine.py player.py scripts\check_environment.py
python scripts\check_environment.py --profile dev
python scripts\check_environment.py --profile gst
```

Acceptance criteria:

- The working tree is clean before the block starts.
- `HEAD` is `6f36888` or a direct, reviewed descendant.
- Unit tests pass without a real DASH server, display server, GStreamer, external network, media files, ML tooling, or `config/client.local.yaml`.
- Python compilation passes on the listed runtime modules.
- The `dev` environment profile passes.
- The non-strict `gst` profile may warn when GStreamer/PyGObject are absent, but it must not fail.
- GStreamer is not required on Windows.

## Ubuntu Acceptance Checklist

Run from the repository root on the Ubuntu client environment:

```bash
git status --short --branch
git rev-parse --short HEAD
python -m unittest discover
python -m py_compile main.py core/client_config.py core/controller/registry.py core/controller/base.py core/controller/contract.py core/controller/fixed_quality.py core/controller/scripted_quality.py core/run_context.py core/runtime_feedback.py core/dataset_schema.py core/benchmark_contract.py core/output_artifacts.py core/media_engine/base.py core/media_engine/fake.py core/media_engine/gst_media_engine.py player.py scripts/check_environment.py
python scripts/check_environment.py --profile dev
python scripts/check_environment.py --profile gst
python scripts/check_environment.py --profile gst --strict
```

Acceptance criteria:

- Unit tests pass with no network, display server, real DASH server, media files, or GUI dependency.
- The `dev` environment profile passes.
- The non-strict `gst` profile exits successfully even when optional pieces are absent.
- The strict `gst` profile passes only on a machine intentionally prepared with GStreamer/PyGObject.
- Optional fake and GStreamer runtime checks with real MPDs are manual operational checks, not unit tests and not final benchmark results.

## Fake Engine Acceptance

The fake media engine is the controlled path for deterministic tests, replay-oriented development, and future benchmark/control work.

Acceptance criteria:

- It remains import-safe and testable on Windows and Ubuntu.
- Offline smoke tests exercise the config-driven `main.main(argv)` path with a temporary MPD and patched downloader.
- It does not require a real DASH server, external network, GStreamer, a display server, media files, GUI, ML tooling, or `config/client.local.yaml`.
- Its outputs are validation/control artifacts and must not be compared with GStreamer outputs as equivalent benchmark data.

## GStreamer Acceptance

GStreamer is an integration/demo path. It proves that the client can feed a real media pipeline on a prepared Ubuntu machine, but it is not benchmark-grade in Phase 1.

Acceptance criteria:

- Importing `core.media_engine.gst_media_engine` remains safe without local GStreamer/PyGObject.
- Missing GStreamer/PyGObject diagnostics point users back to `media_engine.name: fake` and the strict Ubuntu GST check.
- Explicit missing sink/plugins fail clearly rather than silently falling back to another sink.
- Headless GST with `decode_video=false` and `fakesink` is structural validation only.
- Headless GST with `decode_video=false` and `fakesink` may complete faster than real time and must not be used for playback-timing QoE or benchmark timing.
- Visible playback with `decode_video=true` and a video sink such as `autovideosink` is optional demo validation. It proves integration on that machine, not academic benchmark validity.
- GStreamer queue underrun/stall signals are runtime diagnostics and are not automatically QoE rebuffer events.
- Fake-engine and GStreamer outputs must not be mixed as equivalent benchmark runs.

## Output Acceptance

Current canonical run artifacts are:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `segment_telemetry.csv`
- `evaluation_segments.csv`
- `run.log`

`segment_telemetry.csv` and `evaluation_segments.csv` are validation/evaluation artifacts, not final benchmark result tables. `evaluation_segments.csv` is not a final AI training dataset. Rows with `use_for_eval=false` are not benchmark rows. Terminal drain stalls are not steady-state rebuffering.

Legacy names `dataset.csv` and `dataset_training.csv` are deprecated compatibility/historical names. New default runs must not produce them and current docs must not present them as canonical outputs.

## Not Implemented Yet

Phase 1 acceptance explicitly does not mean that the following exist:

- academic ABR baselines;
- AI-based ABR;
- PPO or any other training loop;
- final QoE metric;
- final reward definition;
- trace infrastructure;
- Mahimahi or network-emulation infrastructure;
- benchmark scripts;
- final AI training dataset;
- GUI/operator dashboard.

`fixed_quality` and `scripted_quality` are deterministic test/debug controllers. `max_quality` remains legacy/debug/stress behavior. None of them is an academic baseline.

## Next Phase Recommendation

After closing Phase 1 through the Block 14 readiness gate, return to Phase 0 methodology work before implementing baseline controllers. Classical ABR controllers should be implemented only after their primary papers/specifications and benchmark methodology decisions are documented.
