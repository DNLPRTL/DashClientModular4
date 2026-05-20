# Replay Runner Requirements

This file defines requirements for a future trace-driven runner. It does not implement that runner.

## Required Properties

| property | requirement |
| --- | --- |
| Determinism | Same controller, trace, config and commit should produce the same future run artifacts. |
| Controller neutrality | Runner must not require controller-specific code paths. |
| Unit clarity | Trace input units must be explicit and converted before execution. |
| Time model clarity | Runner must document how trace time maps to segment download time. |
| Synthetic-first validation | Runner must pass synthetic trace tests before real trace use. |
| Artifact manifest | Future runs must record controller, trace ID, commit, config and method. |
| Repository hygiene | Raw traces, logs, CSVs, ZIPs and media stay outside git. |
| Python compatibility | Future code must remain compatible with the project Python version policy. |

## Candidate Normalized Trace Schema

This schema is only a requirement draft, not an implemented format.

| field | meaning |
| --- | --- |
| `trace_id` | Stable external or local identifier. |
| `sample_time_s` | Monotonic seconds from trace start. |
| `throughput_bps` | Available throughput in bits per second. |
| `source_dataset` | Dataset ID from `trace_dataset_matrix.md`. |
| `split` | train, validation, test, OOD or synthetic. |
| `notes` | Optional non-controller metadata. |

## Forbidden Shortcuts

- Do not infer final QoE/reward in the runner.
- Do not pass GPS, RSRP, RSRQ, SINR or other context fields into existing controllers.
- Do not change parser, downloader, buffer, player or media engines to fit a dataset.
- Do not write generated artifacts into tracked documentation folders.
- Do not use `pytest` for this project.

## Future Acceptance Evidence

Before real traces are used, a future runner should have:

1. unit tests based on synthetic traces;
2. deterministic output checks;
3. schema validation checks;
4. artifact manifest checks;
5. documentation of unsupported trace features;
6. client readiness check passing in strict mode.

## Phase 3.2A Source-Triage Update

The future runner must not be implemented in this block. Requirements now fixed:

- accept an internal trace schema rather than raw dataset formats;
- support deterministic synthetic traces;
- emit canonical run artifacts;
- record trace id, source dataset id, converter version and split label;
- run with `unittest` without external network;
- avoid requiring root/admin privileges;
- keep Mahimahi/netem behind optional runbooks;
- separate trace replay from final QoE/reward calculation until Phase 3.5.
