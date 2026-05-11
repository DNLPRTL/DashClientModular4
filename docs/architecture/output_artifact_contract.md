# Output Artifact Contract

Date: 2026-05-11

This contract names the current run artifacts for Phase 1 hardening. It is an output hygiene contract, not a benchmark methodology.

Column-level provenance for `segment_telemetry.csv` and `evaluation_segments.csv` is documented in `docs/architecture/telemetry_column_provenance.md`. Console/progress output is covered separately by `docs/architecture/runtime_console_output_contract.md` and is not a canonical artifact.

| Artifact name | Purpose | Source module | Benchmark / evaluation role | Canonical? | Legacy / deprecated? | Notes / risks |
|---|---|---|---|---|---|---|
| `run_manifest.json` | Run index with config, environment, git, output paths, and neutrality metadata. | `core.run_context` | Helps audit a run; not a score. | Yes | No | Must use clear output keys and must not advertise `dataset` or `training` as canonical outputs. |
| `config.resolved.json` | Resolved config after defaults and local overrides. | `core.run_context`, `core.client_config` | Reproducibility context only. | Yes | No | May contain local MPD URLs; do not commit generated runs. |
| `environment.json` | Python, platform, package, optional analysis, optional GStreamer, and git snapshot. | `core.run_context` | Reproducibility context only. | Yes | No | GStreamer availability does not make a run benchmark-grade. |
| `segment_telemetry.csv` | Full per-segment/runtime telemetry. | `player.py`, `core.dataset_schema` | Raw validation/control telemetry; rows are benchmark-eligible only when `use_for_eval=true`. | Yes | Replaces `dataset.csv`. | Contains runtime/debug and pending-semantics fields. Do not treat the whole file as benchmark results. |
| `evaluation_segments.csv` | Compact evaluation-oriented segment records with `eval_phase` and `use_for_eval`. | `player.py`, `core.dataset_schema` | Candidate input for later evaluation tooling; not final IA training data. | Yes | Replaces `dataset_training.csv`. | The name is intentionally not "training" because no final training pipeline exists. |
| `run.log` | Run-specific Python log. | `main.py` logging setup | Debug/reproducibility aid only. | Yes | No | Console output still appears normally. |
| `dataset.csv` | Historical full telemetry filename. | Deprecated compatibility only | None as a canonical output. | No | Yes | New default runs must not produce this file. |
| `dataset_training.csv` | Historical compact CSV filename. | Deprecated compatibility only | None as a canonical output. | No | Yes | Misleading because no final IA training dataset exists yet. New default runs must not produce this file. |

## Interpretation Rules

Run outputs are not automatically benchmark results. They are validation/control artifacts until Phase 1 acceptance, final QoE/reward methodology, baseline controllers, and benchmark scripts are defined.

`segment_telemetry.csv` is runtime and per-segment telemetry. It includes useful context, debug columns, and pending-semantics columns. Use `eval_phase` and `use_for_eval` to distinguish rows that are allowed for evaluation from startup, warm-up, drain, terminal, init, and error rows.

`evaluation_segments.csv` is evaluation-oriented segment data. It is not a final IA training dataset, and it does not imply that a final training pipeline, reward definition, or academic comparison protocol exists.

Rows with `use_for_eval=false` are not benchmark rows. Terminal drain stalls are not steady-state rebuffering. No final QoE/reward exists yet. No final IA training dataset exists yet. No academic baseline comparison exists yet.

Fake-engine outputs and GStreamer outputs must not be mixed as equivalent benchmark results. The fake engine is the controlled path for deterministic tests and future replay/control work. GStreamer remains an integration/demo path and is not benchmark-grade in this block; headless `decode_video=false`/`fakesink` validation can complete faster than real time and must not be used for playback-timing QoE.
