# Phase 3.2C Dataset Audit Summary

This document summarizes the local raw dataset audit. It is authored documentation, not a generated inventory.

## Audit Input

The only acquisition evidence used in Phase 3.2C is the provided local audit summary generated on:

```text
2026-05-21T14:43:00.9062026+02:00
```

Expected repository base:

```text
5a8cc4c docs(science): define Phase 3 common trace schema
```

## Dataset Audit Table

| priority | dataset_id | acquisition decision | file_count | total_size_mb | raw path policy |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `hsdpa_norway_mmsys2013` | acquired first local raw candidate | 98 | 4.494 | outside repo |
| 2 | `ghent_4g_lte_bandwidth_logs` | acquired second local raw candidate | 9 | 0.773 | outside repo |
| 3 | `lancaster_abr_throughput_traces` | acquired third local raw candidate | 2 | 2.13 | outside repo |

## Risks Discovered From Acquisition

| dataset | risk | implication |
| --- | --- | --- |
| HSDPA Norway | route folders and report logs imply route-level grouping is required | split policy must group by route/trace before any windowing |
| Ghent 4G/LTE | source files are ZIP archives by mobility mode | later block must inspect archives outside repo and define safe extraction/conversion policy |
| Lancaster | source is ZIP plus README | later block must inspect archive contents and repository terms before conversion |
| all acquired sources | raw files are outside repo but include logs/ZIPs | repo must keep only authored Markdown summaries |
| all acquired sources | acquisition does not prove schema validity | schema validation waits for Phase 3.3A synthetic fixtures and later converter work |

## Current Phase Decisions

- HSDPA Norway, Ghent 4G/LTE and Lancaster are now local raw candidates because they are acquired outside the repository.
- These files are not normalized traces.
- These files are not final benchmark artifacts.
- These files are not assigned to final train/validation/test/OOD splits.
- Raca 4G, Raca 5G and Lumos5G remain deferred/OOD acquisition candidates.
- FCC MBA remains reference-only.
- Puffer remains metadata-only.

## Next Gates

Before converter implementation:

1. close Phase 3.2C documentation;
2. confirm raw files remain outside repo;
3. define synthetic schema validation in Phase 3.3A;
4. keep conversion implementation scoped to a later explicit block;
5. preserve `normalized_trace_schema_v1` and manifest contracts.

Before replay runner implementation:

1. complete converter/schema validation evidence;
2. define trace loading boundaries;
3. prove no future-sample leakage through tests;
4. keep QoE/reward deferred to Phase 3.5;
5. keep Mahimahi and `tc/netem` as candidates, not mandatory benchmark paths.

## Memory And Defense Usage

Use this audit to state that the first trace candidates are locally available outside git. Do not claim they have been normalized, validated, replayed or used for benchmark ranking.

