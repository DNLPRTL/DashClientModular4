# rate_based Controller API Mapping

## Contract Summary

The future `rate_based` controller uses the current dict-based controller API. It receives feedback with `setPlayerFeedback()` and returns a target rate in bytes per second from `calcControlAction()`.

## Signal Mapping

| signal in paper | signal in DashClientModular4 | exists / derivable / missing / forbidden | paper unit | client unit | conversion | source document or runtime source | restrictions | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| available bitrates | `rates` | exists | bps in DASH literature | bytes_per_second_list | compare directly in bytes/s; do not multiply by 8 unless source value is in bits/s | `baseline_entry_contract.md`, `core.runtime_feedback` | ladder must come from MPD/client state | use |
| current bitrate | `cur_rate`, `cur_bitrate` | exists | bps | bytes_per_second | use `cur_rate`; treat `cur_bitrate` as legacy alias | `baseline_entry_contract.md` | names are legacy but units are bytes/s | use with caution |
| current quality | `level` | exists | representation index | representation_index | none | controller feedback | must stay within ladder | use |
| segment fetch time (SFT) | `last_download_time` | exists | seconds | seconds | none | downloader/player feedback | must be positive and finite | use |
| media segment duration (MSD) | `fragment_duration` | exists | seconds | seconds | none | parser/player feedback | media rows only; init rows may be zero | use |
| segment size | `last_fragment_size` | exists | bytes or bits depending paper notation | bytes | if comparing with bps, multiply bytes by 8; preferred controller comparison stays bytes/s | downloader/player feedback | must be positive for update | use |
| measured throughput | `last_fragment_size / last_download_time` | derivable | bps | bytes_per_second | `Bps = bytes / seconds` | `source_evidence.md`, `core.runtime_feedback` | avoid relying only on legacy `bwe` fallback | derive explicitly |
| smoothed throughput | controller state | derivable | bps | bytes_per_second | EWMA over positive measured throughput | implementation spec | deterministic state only | derive |
| ratio `mu = MSD / SFT` | `fragment_duration / last_download_time` | derivable | ratio | ratio | no unit conversion | `source_evidence.md` | explanatory; not required for target-rate output | optional |
| buffer guard | `queued_time` | exists | seconds | seconds | none | media engine feedback | guard only, not primary decision | use as safety guard |
| TCP RTT | none | forbidden | seconds | none | none | prohibited by source evidence | no network-layer instrumentation | do not use |
| packet loss | none | forbidden | ratio/count | none | none | prohibited by source evidence | no TCP-layer dependency | do not use |
| server/sender state | none | forbidden | mixed | none | none | source evidence | client-side only | do not use |
| console output | none | forbidden | text | none | none | runtime console contract | never an input signal | do not use |

## Output Mapping

| output | unit | client path | decision |
| --- | --- | --- | --- |
| target rate | bytes_per_second | `calcControlAction()` return value | return `rates[candidate_level]` |
| chosen quality | representation_index | `quantizeRate(target_rate)` | let shared quantizer map target rate to level |

## API Restrictions

- Do not add feedback keys in the first implementation unless a separate provenance note is created.
- Do not depend on `start_segment_request` or `stop_segment_request`; they are runtime diagnostics.
- Do not read logs, progress labels, or console text.
- Do not alter parser, downloader, media engine, metrics, or output artifact contracts.
