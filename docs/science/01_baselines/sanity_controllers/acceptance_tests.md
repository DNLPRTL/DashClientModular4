# Sanity Controllers Acceptance Tests

| controller | test | input | expected |
| --- | --- | --- | --- |
| min_rate | one-level ladder | `[1000]` | target `1000`, level `0` |
| min_rate | multi-level ladder | `[1000, 2000, 4000]` | target `1000`, level `0` |
| max_rate | one-level ladder | `[1000]` | target `1000`, level `0` |
| max_rate | multi-level ladder | `[1000, 2000, 4000]` | target `4000`, level `2` |
| fixed_rate | exact ladder rate | target `2000`, ladder `[1000, 2000, 4000]` | level `1` |
| fixed_rate | between ladder rates | target `2500`, ladder `[1000, 2000, 4000]` | level `1` |
| fixed_rate | target rate in bps | target `16000 bps`, ladder `[1000, 2000, 4000]` B/s | target `2000`, level `1` |
| fixed_rate | target rate in kbps | target `16 kbps`, ladder `[1000, 2000, 4000]` B/s | target `2000`, level `1` |
| fixed_rate | index below zero | level `-1`, ladder `[1000, 2000, 4000]` | target `1000`, level `0` |
| fixed_rate | index above max | level `99`, ladder `[1000, 2000, 4000]` | target `4000`, level `2` |
| all | invalid ladder | empty, non-numeric, zero, or negative rates | safe target `0.0`, no crash |

## Smoke Requirement

Each sanity controller must pass a deterministic fake-engine run and must not modify parser, downloader, media engine, metrics, configs, or benchmark contracts beyond its own controller registration/configuration.

Smoke validation confirms integration only. It is not benchmark evidence and must not be used to compare algorithms.
