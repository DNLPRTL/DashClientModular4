# Acceptance Tests Template

Create this file before implementing an academic baseline.

## Unit Tests

| test | input | expected | reason |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Fake-Engine Smoke Tests

| test | setup | expected telemetry | failure condition |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Invariants

- Never select a representation outside the ladder.
- Return target rates in bytes per second.
- Keep decisions deterministic for identical feedback and state.
- Do not modify parser, downloader, media engine, metrics, or benchmark code.
- Do not depend on console text.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Ubuntu | TBD when available | pass |
