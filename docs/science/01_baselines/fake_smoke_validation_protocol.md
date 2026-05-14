# Fake Smoke Validation Protocol

Fake smoke tests validate implementation integration. They are not final benchmark results.

## Purpose

The fake engine is the controlled path for Phase 2.3 smoke validation. It should verify that each controller can be selected through config/registry, receive feedback, return contract-compatible actions, and produce canonical run artifacts without breaking client neutrality.

## Required Canonical Artifacts

Every smoke run must produce:

| artifact | required | interpretation |
| --- | --- | --- |
| `run_manifest.json` | yes | Run metadata and neutrality flags, not a score. |
| `config.resolved.json` | yes | Reproducibility context. |
| `environment.json` | yes | Environment snapshot. |
| `run.log` | yes | Debug log, not controller input. |
| `segment_telemetry.csv` | yes | Per-segment telemetry, not final benchmark result. |
| `evaluation_segments.csv` | yes | Evaluation-oriented rows, not training data. |
| `dataset.csv` | no | Deprecated legacy output; must not be produced by default. |
| `dataset_training.csv` | no | Deprecated legacy output; must not be produced by default. |

## Minimum Smoke Scenarios

| scenario | expected validation | benchmark claim allowed? |
| --- | --- | --- |
| stable high capacity | Controller integrates and may select higher levels according to its spec. | No |
| stable low capacity | Controller integrates and stays safe/lower where expected. | No |
| capacity drop | Controller reacts without crashing or invalid level. | No |
| capacity recovery | Controller remains deterministic and contract-compatible. | No |
| low initial buffer/startup | Startup fallback and safety behavior are visible. | No |
| single-representation ladder | Controller selects the only representation. | No |
| short deterministic fake run | Canonical artifacts are produced and readiness still passes. | No |

## Controller-Specific Smoke Focus

| controller | fake smoke focus |
| --- | --- |
| rate_based | Measured throughput path, conservative upshift, aggressive downshift, low-buffer guard. |
| bba | Reservoir/cushion zones with fake buffer levels. |
| bola | BOLA-basic score path without throughput, DYNAMIC or FAST SWITCHING. |
| mpc | Throughput history, buffer simulation and first-action return. |
| robust_mpc | Prediction-error correction and no Pensieve/RL artifacts. |

## Smoke Validation Rules

- Use fake engine only for controlled smoke validation.
- Do not compare fake and GStreamer as equivalent benchmark paths.
- Do not claim paper-level performance.
- Do not define final QoE/reward.
- Do not create traces, replay, emulation or datasets.
- Do not parse console/progress output.
- Validate artifacts through canonical filenames and readiness checks.

## Pass Criteria

A smoke run passes when it completes deterministically, produces canonical artifacts, records controller identity and decisions, avoids deprecated output names, and leaves `python -m unittest discover` plus strict readiness passing.

## Fail Criteria

A smoke run fails if it crashes, produces invalid target rates or levels, depends on console output, writes non-canonical dataset files, mutates metrics, or uses GStreamer timing as benchmark evidence.
