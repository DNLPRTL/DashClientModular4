# Sanity Controllers Acceptance Tests

| controller | test | input | expected |
| --- | --- | --- | --- |
| min_rate | one-level ladder | `[1000]` | target `1000`, level `0` |
| min_rate | multi-level ladder | `[1000, 2000, 4000]` | target `1000`, level `0` |
| max_rate | one-level ladder | `[1000]` | target `1000`, level `0` |
| max_rate | multi-level ladder | `[1000, 2000, 4000]` | target `4000`, level `2` |
| fixed_rate | exact ladder rate | target `2000`, ladder `[1000, 2000, 4000]` | level `1` |
| fixed_rate | between ladder rates | target `2500`, ladder `[1000, 2000, 4000]` | level `1` |
| all | invalid ladder | empty, non-numeric, zero, or negative rates | validation failure |

## Smoke Requirement

After future implementation, each sanity controller must pass a deterministic fake-engine run and must not modify parser, downloader, media engine, metrics, configs, or benchmark contracts beyond its own controller registration/configuration.
