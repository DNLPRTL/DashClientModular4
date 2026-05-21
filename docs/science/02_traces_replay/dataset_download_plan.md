# Dataset Download Plan

Phase 3.2B does not download any dataset. This document defines the policy for a future download block.

## Current Authorization

| source | download now | future external download candidate | reason |
| --- | --- | --- | --- |
| HSDPA Norway / Riiser MMSys 2013 | no | yes, first candidate | Small/classic throughput traces with simple expected conversion. |
| Ghent 4G/LTE Bandwidth Logs | no | yes, first candidate | LTE complement with manageable throughput logs. |
| Lancaster ABR-Throughput-Traces | no | yes, after license/terms review | HAS/live throughput traces useful after first converters. |
| Raca 4G LTE channel/context | no | later | Modern/OOD candidate, but schema and KPI handling are second wave. |
| Raca 5G channel/context | no | later | OOD candidate, but GPL/schema review and grouping policy must close first. |
| Lumos5G | no | later | Strong OOD candidate, but high variability and trajectory leakage require care. |
| FCC MBA | no | no | Reference-only until conversion/download plan exists. |
| Puffer archive | no | no | Metadata-only until conversion, storage and causal plans exist. |

## Future Download Preconditions

A future external download block must confirm:

1. dataset card is complete;
2. license or usage terms are documented;
3. raw storage path is outside the repository;
4. conversion target is `normalized_trace_schema_v1`;
5. leakage grouping is defined before split assignment;
6. generated files remain outside git;
7. no controller, player, runtime, media-engine or metric changes are required.

## Download Locations

Raw candidates must use:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_raw_candidates
```

Normalized traces must use:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_normalized\schema_v1
```

Manifests must use:

```text
C:\Users\danie\Documents\TFG\_datasets\phase3_traces_replay\_manifests
```

## Repository Rule

No real raw trace, normalized trace, generated manifest, log, CSV, ZIP, PDF or media file is added to the repository by the download process.

## Phase 3.2C Local Acquisition Update

The Phase 3.2C audit records local raw acquisition outside the repository:

| source | acquired | file_count | total_size_mb | status |
| --- | ---: | ---: | ---: | --- |
| HSDPA Norway / Riiser MMSys 2013 | true | 98 | 4.494 | first local raw candidate |
| Ghent 4G/LTE Bandwidth Logs | true | 9 | 0.773 | second local raw candidate |
| Lancaster ABR-Throughput-Traces | true | 2 | 2.13 | third local raw candidate |

These files remain raw local datasets outside git. They are not normalized, not benchmark artifacts, and not assigned to final splits.

Raca 4G, Raca 5G and Lumos5G remain deferred/OOD acquisition candidates. FCC MBA remains reference-only. Puffer remains metadata-only.
