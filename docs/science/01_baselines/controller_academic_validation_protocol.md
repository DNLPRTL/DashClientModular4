# Controller Academic Validation Protocol

This protocol defines what counts as a valid academic implementation once Phase 2.3 starts. A runnable controller is not enough; it must also be scientifically traceable and defensible.

## Valid Implementation Criteria

| criterion | requirement | invalidating example |
| --- | --- | --- |
| Paper family match | The implementation matches the source family and documented simplification. | Calling a throughput hybrid `bba`. |
| Allowed signals | Only signals permitted by the controller API mapping are used. | Using TCP RTT in `rate_based`. |
| Unit correctness | Target rates are bytes per second and quality levels are representation indices. | Returning bits per second to `quantizeRate`. |
| Determinism | Identical feedback and controller state produce identical decisions. | Random choice without seed/control. |
| Edge handling | Missing or invalid inputs fail safely as specified. | Crashing on missing throughput history. |
| Explainability | Each decision path can be explained from formulas, parameters and state. | Hidden magic constants not present in specs. |
| Logging/provenance | Enough diagnostic information can be traced through canonical artifacts or documented controller-local fields. | Depending on console text. |
| Chapter 5 defense | The implementation can be described in the implementation chapter with source mapping. | Code behavior differs from `implementation_spec.md`. |
| Chapter 6 readiness | Later evaluation can reuse outputs without changing the scientific claim. | Controller writes custom benchmark CSVs. |
| Claim boundary | No final benchmark claim before later methodology. | Saying BOLA beats BBA from smoke tests. |

## Validation Levels

| level | evidence | what it proves | what it does not prove |
| --- | --- | --- | --- |
| Documentation gate | Required Markdown exists and is coherent. | The implementation can start from distilled sources. | Code correctness. |
| Unit tests | Formula, contract and edge-case tests pass. | Decision logic matches spec in controlled inputs. | Runtime performance. |
| Fake smoke | Fake-engine run completes with canonical artifacts. | Integration with client loop and artifact path works. | Real-network superiority or paper-level performance. |
| Readiness check | Existing client readiness remains green. | Client neutrality was not broken. | Final QoE or benchmark validity. |
| Future benchmark | Trace/replay and final QoE methodology, later phase. | Comparative claims under defined methodology. | Out of scope for Phase 2.3 smoke tests. |

## Controller-Specific Academic Boundaries

| controller | must preserve | must not claim |
| --- | --- | --- |
| rate_based | Throughput-based selection from application-layer segment measurements. | Network-layer capacity estimation or final QoE quality. |
| bba | Buffer-map behavior with reservoir and cushion. | Netflix production equivalence. |
| bola | BOLA-basic utility/buffer score. | dash.js DYNAMIC, FAST SWITCHING or production BOLA-E. |
| mpc | Receding-horizon enumeration with internal provisional objective. | Final TFG QoE/reward. |
| robust_mpc | MPC plus recent prediction-error correction. | Pensieve/RL implementation. |

## Decision Explanation Requirement

Every future controller implementation should be explainable with:

1. Input feedback values and units.
2. Controller parameters and defaults.
3. Intermediate estimate or score.
4. Selected target rate in bytes per second.
5. Quantized representation index.
6. Safe fallback path if any input is invalid.

## Rejection Conditions

Reject an implementation if it changes player behavior, metrics, parser, downloader, media engine, output artifacts, or configs without a separate approved scope. Reject it also if it uses forbidden signals, reads console output, creates benchmark claims, downloads datasets, adds PDFs, or introduces AI/RL components outside the approved phase.
