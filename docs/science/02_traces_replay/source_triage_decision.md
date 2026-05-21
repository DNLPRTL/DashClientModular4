# Phase 3.2A source triage decision

## Status

Phase 3.2A closes the initial source triage for trace datasets, replay/emulation methods, real-world methodology and threats to trace-driven validity.

This document is documentation-only. It does not authorize replay implementation, dataset download, benchmark ranking, final QoE/reward, controller changes, player changes or media-engine changes.

## Base context

- Phase 1: closed.
- Phase 2: closed with controllers `min_rate`, `fixed_rate`, `max_rate`, `rate_based`, `bba`, `bola`, `mpc`, `robust_mpc`.
- Phase 3.1: scaffold closed at `1df5389 docs(science): scaffold Phase 3 trace replay methodology`.

## Accepted mandatory method cards

| id | source | decision | reason |
| --- | --- | --- | --- |
| method_mahimahi | Mahimahi | mandatory card; candidate secondary validation path | Canonical HTTP record-and-replay/emulation reference; useful but not first implementation target. |
| method_pensieve_eval | Pensieve trace-driven evaluation | mandatory card; methodology only | Anchors ABR trace-driven methodology and relates to existing controllers; no IA/RL implementation in Phase 3. |
| method_puffer | Puffer/Fugu learning in situ | mandatory card; real-world methodology reference | Warns that simulator/emulator results may not generalize to real Internet paths. |
| method_tc_netem | Linux tc/netem | mandatory card; Linux fallback | Lightweight impairment alternative for Ubuntu-only experiments; not default runner. |
| method_causalsim | CausalSim | mandatory card; validity-threat reference | Documents exogenous-trace assumption and bias risk in trace-driven simulation. |

## Accepted optional/recommended method cards

| id | source | decision | reason |
| --- | --- | --- | --- |
| method_veritas | Veritas | optional/recommended card | Supports causal warning for video streaming traces without opening implementation. |
| method_wei2019 | Wei et al. trace-based emulation | optional/recommended card | Supports controlled identical-condition trace-based emulation methodology. |
| method_into_wild | Into the Wild / ABR-Arena | optional/recommended card | Future generalization and real-world diversity reference for ML-based ABR. |

## Accepted mandatory dataset/source cards

| id | source | decision | reason |
| --- | --- | --- | --- |
| hsdpa_norway | Norway HSDPA / Riiser MMSys 2013 | first-real-integration candidate | Small/classic/ABR-relevant throughput logs with simple format. |
| ghent_4g_lte | Ghent 4G/LTE Bandwidth Logs | first-real-integration candidate | LTE complement with similar log concept and realistic mobile variation. |
| lancaster_has | Lancaster ABR-Throughput-Traces | first-benchmark-design candidate | Large HAS/live throughput trace set, likely useful after first converters. |
| raca_4g | Raca 4G LTE channel/context dataset | modern-mobile/OOD candidate | Public 4G dataset with KPIs and one-second throughput; more complex than first targets. |
| raca_5g | Raca 5G channel/context dataset | 5G OOD candidate | Public 5G dataset with application patterns; GPL/schema review needed. |
| lumos5g | Lumos5G | high-variability 5G OOD candidate | Strong 5G/mmWave generalization source; not first runner target. |
| fcc_mba | FCC Measuring Broadband America | reference-only | Historically important for Pensieve-style broadband context; no raw download now. |
| puffer_data | Puffer data archive | metadata-only | Valuable real-world source but high storage/integration/causal risk. |

## Promoted sources

- CausalSim is promoted to mandatory because Phase 3 must explicitly document bias in naive trace-driven simulation.
- Ghent 4G/LTE is promoted to mandatory card because it is a practical LTE complement to the Norway HSDPA traces.
- Lancaster ABR-Throughput-Traces is promoted to mandatory card because it is directly HAS/live throughput oriented and large enough to influence later benchmark design.

## Deferred or rejected for this block

| source family | decision | reason |
| --- | --- | --- |
| Full Puffer raw daily data | deferred | High storage, schema and causal complexity. Metadata-only now. |
| Raw FCC MBA data | deferred | Historical broadband reference; conversion/storage plan required first. |
| Mahimahi implementation | deferred | Candidate method only; first implementation should be a Python trace-driven runner. |
| tc/netem implementation | deferred | Useful fallback but not safe/default unit-test path. |
| CausalSim/Veritas implementation | rejected for Phase 3.2A | Methodological threat references only; causal implementation is out of scope. |
| IA/RL ABR papers and systems | deferred to Phase 4/6 | Do not open IA before replay/traces/QoE methodology. |
| ns-3/Mininet/full network simulators | deferred | Too heavy for current phase and not needed before simple replay is validated. |
| GStreamer benchmark | rejected | GStreamer remains integration/demo, not benchmark-grade. |

## Operational decision

First implementation path after Phase 3.2A should be a custom Python trace-driven fake/replay runner, because it can be deterministic, tested with `unittest`, and run on Windows/Ubuntu without privileged network setup.

Secondary validation path: Mahimahi on Ubuntu, only if the custom runner and trace schema are stable.

Fallback/alternative path: Linux `tc/netem`, only with isolated runbook and no default test dependency.

## Non-goals confirmed

- No replay runner implementation.
- No dataset download.
- No final QoE/reward.
- No benchmark ranking.
- No IA/RL.
- No controller/player/runtime/media-engine changes.
- No PDF/dataset/generated artifact committed.

## What this unlocks

Phase 3.2B can now design the common internal trace schema, conversion plan and synthetic trace requirements before any code is written.

## Phase 3.2B Schema Update

Phase 3.2B uses the triage decisions above to define the internal trace schema and conversion plan:

- first real integration candidates remain HSDPA Norway, Ghent 4G/LTE and Lancaster;
- modern/OOD candidates remain Raca 4G, Raca 5G and Lumos5G;
- FCC remains reference-only;
- Puffer remains metadata-only;
- no dataset becomes final benchmark material;
- no final split is closed;
- no download, converter or runner is implemented.

The active input contract is `normalized_trace_schema_v1`, documented in `common_trace_schema.md`.
