# Trace Replay Source Inventory

This inventory records Phase 3.1 source decisions. A row in this file is not permission to download a dataset, implement replay, define QoE or run a benchmark.

## Source Categories

| category | meaning | Phase 3.1 rule |
| --- | --- | --- |
| mandatory | Must be examined and carded before Phase 3 closes. | Required for methodology or core dataset justification. |
| recommended | Strong candidate for dataset breadth or modernity. | Card if selected by the search and selection protocol. |
| optional | Useful later, but not needed to unblock Phase 3.1. | Keep metadata only unless Phase 3 selection promotes it. |
| rejected/deferred | Not suitable for immediate Phase 3 trace/replay work. | Do not download, implement or cite as final evidence unless re-opened. |

## Mandatory Sources

| id | type | source | year | DOI/URL | Phase 3 role | initial decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TR-M01 | method paper/tool | Netravali et al., Mahimahi: Accurate Record-and-Replay for HTTP | 2015 | https://www.usenix.org/conference/atc15/technical-session/presentation/netravali | HTTP record-and-replay methodology candidate | mandatory method card | Method candidate only; not mandatory implementation yet. |
| TR-M02 | ABR methodology paper | Mao et al., Neural Adaptive Video Streaming with Pensieve | 2017 | https://doi.org/10.1145/3098822.3098843 | Trace/replay/evaluation methodology reference | mandatory source card | Use only for trace, simulator, replay and evaluation methodology. No IA/RL implementation in Phase 3. |
| TR-M03 | dataset paper/source | Riiser et al., Commute Path Bandwidth Traces from 3G Networks | 2013 | https://qualinet.github.io/databases/commute_path_bandwidth_traces_from_3g_networks/ | Classic Norway HSDPA path bandwidth traces | mandatory dataset card | Small, ABR-relevant, and used by Pensieve-like methodology. Do not download in Phase 3.1. |
| TR-M04 | reference dataset source | FCC Measuring Broadband America | ongoing | https://www.fcc.gov/general/measuring-broadband-america | Reference broadband source | mandatory reference card | Reference-only until a conversion and download plan exists. |
| TR-M05 | deployment/evaluation paper | Yan et al., Puffer / Learning in situ | 2020 | https://www.microsoft.com/en-us/research/publication/puffer/ | In-situ ABR evaluation and real deployment methodology | mandatory source card | Methodological warning against overclaiming from emulators. |
| TR-M06 | dataset description | Puffer data description | ongoing | https://puffer.stanford.edu/data-description/ | Metadata for Puffer data schema and statistical cautions | mandatory metadata card | Metadata-only in Phase 3.1; full raw daily data is deferred. |
| TR-M07 | system manual | Linux `tc/netem` manual | current manual | https://man7.org/linux/man-pages/man8/tc-netem.8.html | Linux network emulation candidate | mandatory method card | Fallback or complementary method candidate; platform and privilege constraints must be evaluated. |

## Recommended Sources

| id | type | source | year | DOI/URL | Phase 3 role | initial decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TR-R01 | dataset | 4G/LTE Bandwidth Logs, Ghent, Belgium | 2016 | https://users.ugent.be/~jvdrhoof/dataset/ | Lightweight 4G mobile throughput candidate | recommended dataset card | Likely useful for small modern mobile scenarios. |
| TR-R02 | dataset paper | Raca et al., Beyond Throughput: a 4G LTE Dataset with Channel and Context Metrics | 2018 | https://doi.org/10.1145/3204949.3208123 | 4G trace dataset with channel/context metrics | recommended dataset card | Likely OOD or modern mobile candidate; storage and license must be checked. |
| TR-R03 | dataset paper | Raca et al., Beyond Throughput, the next Generation: a 5G Dataset with Channel and Context Metrics | 2020 | https://doi.org/10.1145/3339825.3394938 | 5G trace dataset with channel/context metrics | recommended dataset card | Likely OOD or modern mobile candidate; conversion risk may be higher. |
| TR-R04 | dataset/project | Narayanan et al., Lumos5G | 2020 | https://networking.umn.edu/lumos5g | Commercial mmWave 5G throughput and context candidate | recommended source card | Good OOD/generalization reference; dataset terms must be checked before use. |
| TR-R05 | dataset | Lancaster ABR-Throughput-Traces | 2021 repository, 2020/2024 papers | https://github.com/lancs-net/ABR-Throughput-Traces | Live HAS realism candidate | recommended dataset card | Likely useful for live/HAS realism; repository asks users not to redistribute. |

## Optional Or Deferred Sources

| id | type | source | status | decision | notes |
| --- | --- | --- | --- | --- | --- |
| TR-O01 | dataset | Full Puffer raw daily data | available externally | optional/deferred | Metadata-only in Phase 3.1 because storage, filtering, privacy, statistics and conversion costs are high. |
| TR-O02 | method papers | Cellular replay extensions such as CellReplay/Sentosa-style recent papers | search later | optional/deferred | Revisit if Mahimahi, `tc/netem` and fake-runner requirements are insufficient. |
| TR-O03 | generalization papers | ML generalization papers from 2024-2026 | search later | optional/deferred | Revisit in Phase 4/6 if IA/RL or learned predictors are introduced. |
| TR-O04 | QoE datasets | Subjective QoE datasets without directly reusable throughput traces | search later | rejected/deferred for Phase 3.1 | Do not use as trace/replay inputs; may be relevant only after final QoE/reward work starts. |

## Hard Rules

- No raw PDFs are added to the repository.
- No datasets are downloaded into the repository.
- No source in this inventory defines the final QoE/reward.
- No source authorizes controller, player, media-engine or metric changes.
- Every promoted dataset must receive a dataset card before use.
- Every promoted replay/emulation method must receive a method card before implementation.

## Phase 3.2A Source-Triage Update

Phase 3.2A locks the first source-triage pass from the distilled Markdown pack. This update adds cards and triage decisions only. It does not authorize PDF storage, dataset download, replay implementation, final QoE/reward, benchmark ranking, IA/RL, or runtime changes.

| id | title/name | type | status | PDF required | dataset download now | target document | decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `netravali2015mahimahi` | Mahimahi: Accurate Record-and-Replay for HTTP | method/tool paper | mandatory | yes | no | `method_cards/mahimahi_record_replay_http.md` | candidate secondary validation path |
| `mao2017pensieve_eval` | Neural Adaptive Video Streaming with Pensieve | methodology paper | mandatory | yes | no | `method_cards/pensieve_trace_driven_evaluation.md` | methodology only, no IA implementation |
| `yan2020puffer` | Learning in situ: a randomized experiment in video streaming | method/deployment paper | mandatory | yes | no | `method_cards/puffer_learning_in_situ.md` | real-world methodology reference |
| `linuxTcNetemManual` | Linux tc-netem manual | tool documentation | mandatory | no | no | `method_cards/tc_netem_network_emulation.md` | fallback/alternative |
| `alomar2023causalsim` | CausalSim: A Causal Framework for Unbiased Trace-Driven Simulation | validity methodology paper | mandatory | yes | no | `method_cards/causalsim_trace_driven_bias.md` | trace-bias threat reference |
| `bothra2023veritas` | Veritas: Answering Causal Queries from Video Streaming Traces | causal methodology paper | recommended | yes | no | `method_cards/veritas_causal_queries_video_streaming_traces.md` | optional/future methodology |
| `wei2019traceBasedEmulation` | Evaluation of Throughput Prediction for Adaptive Bitrate Control Using Trace-Based Emulation | emulation methodology paper | recommended | yes | no | `method_cards/wei2019_trace_based_emulation_for_abr.md` | optional methodology support |
| `hoffman2025intoTheWildABR` | Into the Wild: Real-World Testing for ML-Based ABR | generalization methodology paper | recommended | yes | no | `method_cards/into_the_wild_abrarena_real_world_testing.md` | future generalization reference |
| `riiser2013commutePath` | Commute Path Bandwidth Traces from 3G Networks | dataset paper | mandatory | yes | no | `trace_dataset_cards/hsdpa_norway_mmsys2013.md` | first-real-integration candidate |
| `vanDerHooft2016ghent4g` | 4G/LTE Bandwidth Logs / HTTP/2-based adaptive streaming over 4G/LTE | dataset/paper | mandatory | yes | no | `trace_dataset_cards/ghent_4g_lte_bandwidth_logs.md` | first-real-integration candidate |
| `raca2018beyondThroughput4g` | Beyond Throughput: a 4G LTE Dataset with Channel and Context Metrics | dataset paper | mandatory | yes | no | `trace_dataset_cards/raca_4g_lte_channel_context.md` | modern-mobile/OOD candidate |
| `raca2020beyondThroughput5g` | Beyond Throughput, The Next Generation: a 5G Dataset with Channel and Context Metrics | dataset paper | mandatory | yes | no | `trace_dataset_cards/raca_5g_channel_context.md` | 5G OOD candidate |
| `narayanan2020lumos5g` | Lumos5G: Mapping and Predicting Commercial mmWave 5G Throughput | dataset/method paper | mandatory | yes | no | `trace_dataset_cards/lumos5g_mmwave_throughput.md` | high-variability 5G OOD candidate |
| `lancasterAbrThroughputTraces` | Lancaster ABR-Throughput-Traces | dataset repository | mandatory | no | no | `trace_dataset_cards/lancaster_abr_throughput_traces.md` | HAS/live benchmark-design candidate |
| `fccMeasuringBroadbandAmerica` | FCC Measuring Broadband America | data source | mandatory reference | no | no | `trace_dataset_cards/fcc_measuring_broadband_america_reference.md` | reference-only |
| `pufferDataArchive` | Puffer data archive / puffer-statistics | data archive | mandatory metadata | no | no | `trace_dataset_cards/puffer_data_archive_metadata.md` | metadata-only |
