# bola Controller API Mapping

## Contract Summary

The implemented `bola` controller uses the existing dict-based API and returns a target rate in bytes per second. It computes a controller-internal BOLA-basic score for each representation and stores diagnostic details in `last_metrics`.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| buffer occupancy `Q` | `queued_time` | exists | segments or seconds depending notation | seconds | `Q_segments = queued_time / fragment_duration` | `source_evidence.md`, media engine feedback | fake/GStreamer equivalence not claimed | use |
| segment duration `p` | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | must be positive | use |
| representation set | `rates` | exists | bitrate ladder | bytes_per_second_list | use client bytes/s values | MPD/client state | ladder must be positive and ordered | use |
| segment size `S_m` | optional `segment_sizes_B`, `segment_sizes_bytes`, `segment_size_bytes_by_level`, `representation_sizes_B`, `representation_sizes_bytes`, `size_bytes_by_level` | optional/derivable | bytes | bytes | use exact positive per-level sizes if supplied; otherwise `S_m = rates[m] * fragment_duration` | `source_evidence.md`, `implementation_spec.md` | current player path does not expose a canonical size matrix; disclose VBR limitation | use if present, otherwise derive |
| utility `v_m` | controller utility table | derivable | dimensionless | dimensionless | `ln(rate_m / min_rate)` by default | BOLA spec | internal controller utility, not final QoE | derive |
| `V` | `bola_v`, `V`, or `v` controller parameter | configurable | control scale | controller scale | no conversion | implementation spec | invalid/non-positive values fall back to `5.0` | configure |
| `gamma` | `bola_gamma` or `gamma` controller parameter | configurable | compatible score offset | compatible score offset | no conversion | implementation spec | invalid/non-positive values fall back to `0.2` | configure |
| no-download/wait action | `getIdleDuration()` exists but not selected here | missing for first implementation | seconds/no action | seconds if later used | none in first version | baseline contract | first BOLA-basic does not implement wait | document limitation |
| throughput prediction | `last_fragment_size / last_download_time` | derivable but not primary | bytes/s or bps | bytes_per_second | none if later used | dash.js practical evidence | not primary BOLA-basic signal | do not use initially |
| BOLA-E placeholder segments | none | forbidden initially | player-specific | none | none | dash.js practical evidence | BOLA-E deferred | do not use |
| DYNAMIC mode switch | none | forbidden initially | mixed | none | none | dash.js practical evidence | DYNAMIC deferred | do not use |
| FAST SWITCHING replacement | none | forbidden initially | segment replacement state | none | none | dash.js practical evidence | runtime/scheduler feature, deferred | do not use |
| console output | none | forbidden | text | none | none | runtime console contract | never input | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| target rate | bytes_per_second | `calcControlAction()` | return `rates[best_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | shared quantizer maps rate to level |

## Unit Handling

The runtime ladder is already bytes per second. The controller also accepts optional test/config ladder units through `rates_unit` and converts bits/s, kbps and Mbps to bytes/s before scoring. Target rates returned to the player remain bytes/s.

## API Restrictions

- Do not implement no-download through ad hoc sleeps in this first spec.
- Do not add dash.js scheduler concepts to the client.
- Do not use BOLA utility as final benchmark QoE.
- Do not read or write canonical artifacts inside the controller.
- Do not use `bwe`, `last_fragment_size`, `last_download_time`, TCP RTT/loss/cwnd, server state, future bandwidth or RL/Pensieve fields for BOLA-basic decisions.
