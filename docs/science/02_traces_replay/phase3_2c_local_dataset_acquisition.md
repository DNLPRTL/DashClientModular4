# Phase 3.2C Local Dataset Acquisition

This document records the local acquisition status of the first real trace dataset candidates. It is documentation-only and uses only the audit summary provided for Phase 3.2C.

## Acquisition Purpose

Phase 3.2C confirms whether the first real trace candidates exist locally outside the repository before any converter, TraceLoader or replay runner work begins.

The purpose is to document local raw-candidate availability, storage policy and audit boundaries. The acquired files are not normalized traces, benchmark artifacts, final splits or QoE evidence.

## Local Storage Policy

Raw dataset root outside the repository:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates
```

Machine-readable inventory is local only:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_audit\phase3_2c_local_dataset_acquisition\phase3_2c_local_dataset_inventory.json
```

The JSON inventory must not be committed if it contains raw local paths and full file hashes.

## Acquisition Summary

Generated audit timestamp:

```text
2026-05-21T14:43:00.9062026+02:00
```

| dataset_id | acquired | file_count | total_size_mb | local_raw_path |
| --- | ---: | ---: | ---: | --- |
| `hsdpa_norway_mmsys2013` | true | 98 | 4.494 | `C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates\hsdpa_norway_mmsys2013` |
| `ghent_4g_lte_bandwidth_logs` | true | 9 | 0.773 | `C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates\ghent_4g_lte_bandwidth_logs` |
| `lancaster_abr_throughput_traces` | true | 2 | 2.13 | `C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates\lancaster_abr_throughput_traces` |

## Dataset-By-Dataset Status

### HSDPA Norway / Riiser MMSys 2013

Decision: first local raw candidate because `acquired=true`.

Audit evidence:

- file count: 98;
- total size: 4.494 MB;
- local path outside repo: `C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates\hsdpa_norway_mmsys2013`;
- sample files include route indexes and report logs under route folders such as `routes\bus.ljansbakken-oslo`, `routes\car.aarnes-elverum`, `routes\car.oslo-grimstad` and `routes\car.snaroya-smestad`.

Status: raw local candidate only. Not normalized, not split, not benchmark material.

### Ghent 4G/LTE Bandwidth Logs

Decision: second local raw candidate because `acquired=true`.

Audit evidence:

- file count: 9;
- total size: 0.773 MB;
- local path outside repo: `C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates\ghent_4g_lte_bandwidth_logs`;
- sample files include mode archives such as `logs_bicycle.zip`, `logs_bus.zip`, `logs_car.zip`, `logs_foot.zip`, `logs_train.zip`, `logs_tram.zip`, plus source/index pages.

Status: raw local candidate only. Not normalized, not split, not benchmark material.

### Lancaster ABR-Throughput-Traces

Decision: third local raw candidate because `acquired=true`.

Audit evidence:

- file count: 2;
- total size: 2.13 MB;
- local path outside repo: `C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates\lancaster_abr_throughput_traces`;
- sample files include `ABR-Throughput-Traces.zip` and `README.md`.

Status: raw local candidate only. Not normalized, not split, not benchmark material.

## Deferred Sources

- Raca 4G remains a deferred/OOD acquisition candidate.
- Raca 5G remains a deferred/OOD acquisition candidate.
- Lumos5G remains a deferred/OOD acquisition candidate.
- FCC Measuring Broadband America remains reference-only; no raw download.
- Puffer archive remains metadata-only; no raw daily download.

## Raw-Vs-Normalized Boundary

The acquired local files are raw source files. They are outside the repository and must remain outside the repository.

They are not:

- normalized traces;
- `normalized_trace_schema_v1` files;
- `trace_manifest_v1` records;
- `split_manifest_v1` records;
- benchmark artifacts;
- final train/validation/test/OOD assignments;
- QoE/reward evidence.

## Non-Goals

- no converter implementation;
- no TraceLoader implementation;
- no replay implementation;
- no dataset normalization;
- no final QoE/reward;
- no benchmark ranking;
- no IA/RL;
- no controller/player/runtime/media-engine/metric changes;
- no raw datasets, local JSON inventories, PDFs, ZIPs, CSVs, logs, media or generated artifacts in the repository.

