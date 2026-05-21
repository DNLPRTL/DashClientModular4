# Trace Source To Internal Mapping

This document maps Phase 3.2A dataset/source cards to `normalized_trace_schema_v1`.

The mappings are planning decisions only. They do not download data, implement converters or authorize replay.

## Mapping Table

| dataset/source | source raw format if known | likely conversion input | target normalized columns | unit conversion | expected granularity | expected risks | storage risk | leakage risk | download authorized in next block |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HSDPA Norway / Riiser MMSys 2013 | plain ASCII logs | bytes/ms or equivalent per-sample throughput log | required columns plus `source_dataset`, `source_file`, `network_type`, `mobility_label`, `notes` | bytes/ms or source rate to `throughput_kbps`; time to seconds | about 1 sample/s | final-row duration, route metadata, exact source units | low | medium route leakage | yes, external-only future block after terms check |
| Ghent 4G/LTE Bandwidth Logs | logs | bytes/ms or equivalent throughput log | required columns plus `source_dataset`, `source_file`, `network_type`, `mobility_label`, `notes` | source bytes/rate to `throughput_kbps`; time to seconds | TBD, expected interval samples | mode labels, GPS/context optionality, exact units | low | medium trace/mode leakage | yes, external-only future block after terms check |
| Lancaster ABR-Throughput-Traces | throughput traces | per-trace reported throughput | required columns plus `source_dataset`, `source_file`, `network_type`, `scenario_label`, `notes` | kbps likely kept as-is after validation | TBD, 4 min traces reported | service/day grouping, repository terms, trace count | medium | medium-high service/day leakage | yes, external-only future block after terms check |
| Raca 4G LTE channel/context | KPI dataset files | throughput column plus optional KPI columns | required columns plus optional `network_type`, `operator_or_carrier`, `mobility_label`, `source_file`, `notes` | Mbit/s in paper to `throughput_kbps` | 1 sample/s | context field selection, missing KPI data, grouping | medium | medium operator/device/app leakage | no, second-wave/OOD candidate |
| Raca 5G channel/context | KPI dataset files, public GitHub noted in card | DL/UL bitrate fields and app/context metadata | required columns plus optional `network_type`, `operator_or_carrier`, `mobility_label`, `scenario_label`, `notes` | DL bitrate kbps can map directly after validation | 1 sample/s | license/schema review, app pattern separation, KPI complexity | medium | medium operator/device/app leakage | no, second-wave/OOD candidate |
| Lumos5G | throughput plus features TBD | throughput samples plus trajectory/context fields | required columns plus optional `network_type`, `latitude`, `longitude`, `mobility_label`, `source_file`, `notes` | Mbps/Gbps in paper to `throughput_kbps` | 1 sample/s | high variability, large source, repeated trajectories | medium | medium-high trajectory/location leakage | no, second-wave/OOD candidate |
| FCC Measuring Broadband America | raw releases, derived traces in prior methodology | no conversion input selected | no normalized trace in Phase 3.2B | TBD | TBD | not direct ABR trace source, conversion plan missing | high | medium-high if derived traces are reused naively | no, reference-only |
| Puffer data archive | daily raw/archive logs | no conversion input selected | no normalized trace in Phase 3.2B | chunk/log-derived fields would need causal plan | chunk/session | achieved-throughput bias, storage, schema complexity | high | high causal/log-derived leakage | no, metadata-only |

## Shared Target Columns

Every converted real trace must at least produce:

- `timestamp_s`
- `duration_s`
- `throughput_kbps`

Converters may preserve optional columns when available, but future Phase 3 runner behavior must only require the three mandatory columns.

## Download Meaning

`yes` in the final column means a future block may authorize external download outside the repository. It does not authorize any download in Phase 3.2B and never authorizes committing data to git.

## Phase 3.2C Local Acquisition Update

The audit changes the first three rows from future external candidates to local raw candidates outside the repository:

| dataset/source | local raw status | immediate mapping consequence |
| --- | --- | --- |
| HSDPA Norway / Riiser MMSys 2013 | acquired outside repo | Ready for later raw inspection and converter design after synthetic schema validation. |
| Ghent 4G/LTE Bandwidth Logs | acquired outside repo | Archive contents must be inspected outside repo before converter design. |
| Lancaster ABR-Throughput-Traces | acquired outside repo | Archive/README must be inspected outside repo before converter design. |

No normalized columns are produced in Phase 3.2C. No raw file is copied into the repository.
