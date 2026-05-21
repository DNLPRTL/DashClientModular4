# Trace Directory Layout

This document defines where future raw, normalized and manifest files must live. Phase 3.2B creates no dataset directories and no generated artifacts.

## External Storage Policy

Raw datasets must stay outside the repository:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates
```

Normalized datasets must stay outside the repository:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_normalized\schema_v1
```

Local manifests must stay outside the repository:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_manifests
```

## Repository Policy

The repository may contain:

- authored Markdown documentation;
- dataset cards;
- method cards;
- schema and conversion plans;
- future tiny synthetic fixtures only if explicitly authorized by a later implementation block.

The repository must not contain:

- real raw datasets;
- normalized real traces;
- generated run artifacts;
- PDFs;
- ZIPs;
- logs;
- CSV outputs;
- media files;
- `.venv`, `.idea`, `__pycache__` or `.pyc`.

## Suggested External Layout

The following layout is a future convention, not a created artifact:

```text
_datasets\phase3_traces_replay\
  _raw_candidates\
    hsdpa_norway_mmsys2013\
    ghent_4g_lte\
    lancaster_has\
  _normalized\schema_v1\
    hsdpa_norway_mmsys2013\
    ghent_4g_lte\
    lancaster_has\
  _manifests\
    trace_manifest_v1\
    split_manifest_v1\
```

## Path Hygiene

- Future manifests may record local path policies or external relative paths.
- Thesis/repository documentation should reference dataset ids and trace ids rather than fragile absolute paths when possible.
- Absolute local paths are acceptable in local run manifests, but generated manifests remain outside git unless a later documentation block explicitly summarizes them.

## Phase 3.2C Local Acquisition Update

The audit confirms that the first raw candidates are stored under:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates
```

Observed local raw candidate subfolders:

- `hsdpa_norway_mmsys2013`
- `ghent_4g_lte_bandwidth_logs`
- `lancaster_abr_throughput_traces`

The local audit inventory remains outside the repository under:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_audit\phase3_2c_local_dataset_acquisition
```

Do not commit the local JSON inventory, raw logs, ZIP archives, CSVs, media or generated files.
