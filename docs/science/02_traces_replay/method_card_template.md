# Method Card Template

Create one card per replay or emulation method before implementation.

## Identity

| field | value |
| --- | --- |
| method id | TBD |
| method name | TBD |
| source inventory id | TBD |
| source URL/DOI | TBD |
| method type | replay / emulation / fake trace-driven runner / simulator / hybrid |
| current decision | inventory only / candidate / selected / deferred / rejected |

## Method Role

- Phase 3 role: TBD
- Required for real experiments: yes/no/TBD
- Required for Python unit tests: yes/no/TBD
- Required privileges/platform: TBD
- External dependencies: TBD

## Capabilities

| capability | supported | notes |
| --- | --- | --- |
| trace-driven throughput | TBD | TBD |
| latency control | TBD | TBD |
| loss/reordering control | TBD | TBD |
| HTTP-level replay | TBD | TBD |
| deterministic CI execution | TBD | TBD |
| Windows compatibility | TBD | TBD |
| Linux compatibility | TBD | TBD |
| no-root operation | TBD | TBD |

## Integration Boundary

- Expected integration point: TBD
- Required client changes: none unless later approved
- Controller changes: forbidden
- Metric definition changes: forbidden
- Generated artifact location: outside repo unless summary docs are explicitly authored

## Risks

| risk | level | mitigation |
| --- | --- | --- |
| reproducibility risk | TBD | TBD |
| platform risk | TBD | TBD |
| privilege risk | TBD | TBD |
| complexity risk | TBD | TBD |
| scientific comparability risk | TBD | TBD |

## Decision

- Decision: TBD
- Reason: TBD
- Required next action: TBD
- Explicit non-actions: no implementation in Phase 3.1, no benchmark, no QoE/reward.

