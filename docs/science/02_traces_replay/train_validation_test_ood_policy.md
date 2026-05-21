# Train Validation Test OOD Policy

This policy prevents dataset split ambiguity before any future tuning, learning or IA/RL work.

## Phase 3.1 Position

The implemented Phase 2 controllers are not trained. If Phase 3 only evaluates fixed deterministic controllers, train and validation splits may be marked not applicable. Test and OOD roles still matter for honest reporting.

## Split Definitions

| split | meaning | current use |
| --- | --- | --- |
| train | Traces used to learn model weights or fit parameters. | Not used in Phase 3.1. |
| validation | Traces used to choose parameters, thresholds or model variants. | Not used unless a later phase tunes methods. |
| test | Traces used for final in-domain reporting after choices are frozen. | Candidate role for selected datasets. |
| OOD | Traces from a different domain, technology, route type, collection process or time period. | Candidate role for modern mobile/live realism checks. |

## Split Rules

1. Split by trace identity, not by individual rows inside the same trace, unless a dataset-specific card justifies otherwise.
2. Prefer route/day/session/source-domain separation when metadata is available.
3. Do not let converted derivatives of the same raw trace appear in multiple final roles.
4. Do not use OOD traces to choose final parameters.
5. If a dataset is too small for train/validation/test, document that it is test-only or methodology-only.
6. If no learning or tuning exists, state that train and validation are not applicable.

## Provisional Role Guidance

| source family | provisional role |
| --- | --- |
| Norway HSDPA | likely test or classic baseline-domain candidate after carding |
| Ghent 4G | likely validation/test or mobile OOD candidate |
| Raca 4G/5G | likely OOD candidate unless selected as modern mobile domain |
| Lumos5G | likely OOD/generalization reference |
| Lancaster ABR traces | likely live/HAS realism candidate |
| Puffer raw daily data | deferred; no split role in Phase 3.1 |
| FCC MBA | reference-only; no split role in Phase 3.1 |

## Phase 3.2A Source-Triage Update

No final split is closed in Phase 3.2A.

| source | preliminary role |
| --- | --- |
| synthetic traces | unit tests only |
| HSDPA Norway | first integration / possible legacy-mobile test |
| Ghent 4G/LTE | first integration / possible LTE validation-test |
| Lancaster HAS | possible large validation/test after grouping |
| Raca 4G | possible modern-mobile validation/test/OOD |
| Raca 5G | possible 5G OOD |
| Lumos5G | possible high-variance 5G OOD |
| FCC MBA | reference-only until conversion plan |
| Puffer | metadata-only until conversion/storage/causal plan |

Split rules:

- group by original trace/session/route before windowing;
- never put windows from the same original trace into different train/test roles;
- preserve domain labels;
- reserve OOD before any IA training;
- document every split seed and file list.

## Phase 3.2B Split Manifest Update

`split_manifest_v1` is the future split contract. No final split is closed in Phase 3.2B.

Rules now fixed:

- a `trace_id` must not appear in more than one split;
- dataset-level and route/session-level leakage must be prevented;
- windows from the same original trace must not cross split boundaries;
- future IA train/validation/test/OOD splits must be separated before training starts;
- OOD candidates must include modern mobile/5G traces such as Raca 5G and Lumos5G;
- HSDPA, Ghent and Lancaster are first integration candidates, not final benchmark material by default.
