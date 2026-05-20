# Baseline Smoke Summary

Fake smoke validation checks that controllers integrate with the client loop and produce canonical artifacts. It is not a benchmark, does not compare algorithms and does not define final QoE/reward.

## Phase 2.3 Smoke Status

| controller | smoke status | interpretation |
| --- | --- | --- |
| `min_rate` | required sanity fake smoke path | validates minimum-rate controller integration only |
| `fixed_rate` | required sanity fake smoke path | validates fixed target/level integration only |
| `max_rate` | required sanity fake smoke path | validates maximum-rate controller integration only |
| `rate_based` | standard fake smoke recorded by implementation block docs | validates config/registry/controller/artifact path only |
| `bba` | standard fake smoke recorded by implementation block docs | validates config/registry/controller/artifact path only |
| `bola` | standard fake smoke recorded by implementation block docs | validates config/registry/controller/artifact path only |
| `mpc` | standard fake smoke recorded by implementation block docs | validates config/registry/controller/artifact path only |
| `robust_mpc` | standard fake smoke recorded by implementation block docs | validates config/registry/controller/artifact path only |

Richer low-capacity, capacity-drop, recovery, low-buffer and unstable-capacity scenarios remain deferred until replay/traces or controlled fake scenario fixtures exist.

## Canonical Artifacts

A valid fake smoke run uses temporary run output and verifies the canonical artifact set:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `run.log`
- `segment_telemetry.csv`
- `evaluation_segments.csv`

These artifacts support reproducibility and integration validation. They are not final benchmark outputs.

## Forbidden Generated Artifacts

The following must not be committed or treated as Phase 2.3 outputs:

- `dataset.csv`
- `dataset_training.csv`
- generated runs, logs or CSVs
- media fragments
- local configs
- PDFs

## Interpretation Rules

- Smoke validates integration and canonical artifacts only.
- Smoke does not compare algorithms.
- Smoke does not define final QoE/reward.
- Smoke does not prove paper-level performance.
- Smoke does not make GStreamer benchmark-grade.
- GStreamer remains an integration/demo boundary.
