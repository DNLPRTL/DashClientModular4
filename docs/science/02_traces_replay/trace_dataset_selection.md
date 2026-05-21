# Trace Dataset Selection

No dataset is final until this document is completed and reviewed. Phase 3.1 only creates the selection framework.

## Selection Objective

Choose a small, documented and legally usable trace set that can exercise the implemented Phase 2 controllers under reproducible network conditions. The selected set must support methodology claims before performance claims.

## Required Criteria

| criterion | question | required before final selection |
| --- | --- | --- |
| ABR relevance | Does the dataset represent throughput variation that affects segment download timing? | yes |
| Provenance | Is the source, author, venue or project clear? | yes |
| Availability | Is there a stable access path? | yes |
| License/terms | Can the project use the dataset without redistributing it in git? | yes |
| Format clarity | Are columns, units and sampling interval documented? | yes |
| Conversion plan | Can the data be converted into a future runner input without ambiguous interpretation? | yes |
| Storage hygiene | Can raw data stay outside the repository? | yes |
| Reproducibility | Can selected traces be referenced by ID, checksum or external version? | yes before benchmark |
| Leakage control | Can train, validation, test and OOD roles be separated? | yes if tuning or learning exists |
| Scope fit | Does it avoid forcing controller/player/media/metric changes? | yes |

## Desirable Criteria

- Includes multiple mobility modes or network regimes.
- Includes enough trace duration for several segment decisions.
- Has been used by ABR or HAS papers.
- Has small metadata or sample descriptions that can be reviewed before download.
- Supports both steady and unstable conditions.
- Has a clear citation request.

## Initial Candidate Roles

| candidate | provisional role | rationale |
| --- | --- | --- |
| Norway HSDPA path bandwidth traces | mandatory card, likely first real-trace candidate | Classic, small, ABR-relevant and used by Pensieve-like methodology. |
| Ghent 4G/LTE bandwidth logs | recommended mobile candidate | Lightweight public 4G traces with clear columns and transport modes. |
| Raca 4G LTE dataset | recommended modern mobile/OOD candidate | Adds channel and context metrics. |
| Raca 5G dataset | recommended modern mobile/OOD candidate | Adds 5G channel and context metrics. |
| Lumos5G | recommended OOD/generalization reference | Strong 5G throughput prediction context. |
| Lancaster ABR-Throughput-Traces | recommended live/HAS realism candidate | Derived from live HAS CDN logs, useful for realism if terms allow. |
| Puffer metadata | mandatory metadata/reference | Teaches schema and statistical caution, but raw data is deferred. |
| FCC Measuring Broadband America | mandatory reference-only | Broadband reference source, not a replay input until conversion exists. |

## Decision States

| state | meaning |
| --- | --- |
| inventory only | Source is recorded but not yet carded. |
| card required | A dataset card must be created before further use. |
| metadata only | Only schema and source metadata may be used in Phase 3.1. |
| candidate | Dataset can be considered after carding and license review. |
| selected | Dataset is approved for future external download and conversion. |
| deferred | Dataset is useful later but not in Phase 3.1. |
| rejected | Dataset is not suitable for the current methodology. |

## Final Selection Gate

A dataset may become selected only when:

1. its dataset card is complete;
2. license or usage terms are recorded;
3. raw storage is planned outside git;
4. conversion fields and units are specified;
5. split role is assigned or explicitly marked not applicable;
6. leakage risks are accepted or mitigated;
7. run artifact expectations are compatible with repository hygiene;
8. no controller, player, media engine or metric changes are required.

## Phase 3.2A Source-Triage Update

No dataset is final benchmark material in Phase 3.2A. This update selects candidates and records risks only.

### First-Real-Integration Candidates

1. `hsdpa_norway_mmsys2013`
2. `ghent_4g_lte`
3. `lancaster_has`

These are closer to direct throughput traces, more manageable than full deployment archives, and aligned with ABR/HAS evaluation.

### Modern-Mobile And OOD Candidates

1. `raca_4g_lte_channel_context`
2. `raca_5g_channel_context`
3. `lumos5g_mmwave`

These are useful for generalization and modern cellular conditions, but their schema and context complexity make them second-wave candidates rather than first integration targets.

### Reference-Only And Metadata-Only Sources

1. `fcc_mba_reference`: reference-only until a conversion and download plan exists.
2. `puffer_data_archive`: metadata-only until a conversion, storage and causal plan exists.

### Not Authorized In Phase 3.2A

- No dataset download into the repository.
- No raw Puffer download.
- No raw FCC download.
- No final train/validation/test/OOD split.
- No final QoE/reward.
- No benchmark ranking.

## Phase 3.2B Schema And Conversion Update

Dataset selection now has an additional schema gate: a dataset cannot move from candidate to integration input until it has a documented mapping to `normalized_trace_schema_v1`.

The minimum conversion evidence is:

1. source raw format is identified;
2. unit conversion to `throughput_kbps` is documented;
3. time conversion to `timestamp_s` and `duration_s` is documented;
4. `trace_manifest_v1` fields can be populated;
5. `leakage_group` can be assigned;
6. external raw and normalized storage locations are used;
7. no real dataset file enters the repository.

Phase 3.2B does not select final benchmark material. It only prepares trace inputs and reproducible network conditions for later phases.
