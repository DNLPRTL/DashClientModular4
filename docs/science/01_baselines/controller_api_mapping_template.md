# Controller API Mapping Template

Create this file before implementing an academic baseline.

## Contract

| field | value |
| --- | --- |
| controller API status | current dict-based compatibility API |
| target rate unit | bytes per second |
| quality level unit | representation index |

## Feedback Mapping

| paper signal | client key | canonical alias | unit | available | derivation | risk |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | yes/no | TBD | TBD |

## Output Mapping

| output | unit | client path | notes |
| --- | --- | --- | --- |
| target rate | bytes per second | `calcControlAction()` return value | quantized by base controller |
| chosen level | representation index | `quantizeRate(target_rate)` | must stay within ladder |

## Forbidden Dependencies

- Console output.
- Run log text.
- GStreamer-specific event interpretation as final QoE.
- Direct CSV writes by the controller.
- Runtime metric mutation.
- Unreviewed config changes.
