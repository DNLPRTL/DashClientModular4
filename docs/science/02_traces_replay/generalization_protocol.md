# Generalization Protocol

This protocol defines how future evaluations should reason about in-domain and out-of-distribution traces. It does not run experiments.

## Purpose

Generalization evidence is only meaningful if the project separates:

- traces used to design or tune a method;
- traces used to validate parameters;
- traces used once for final testing;
- OOD traces used to probe robustness outside the selected domain.

Phase 2 controllers are deterministic baselines and are not trained. However, later phases may tune parameters, add learned predictors or introduce IA/RL work. This protocol prevents those later steps from contaminating evaluation.

## Candidate Domains

| domain | example sources | likely role |
| --- | --- | --- |
| legacy mobile | Norway HSDPA | classic ABR-relevant test or baseline domain |
| 4G/LTE mobile | Ghent 4G, Raca 4G | mobile validation/test/OOD |
| 5G mobile | Raca 5G, Lumos5G | modern OOD |
| live/HAS CDN-derived | Lancaster ABR traces | live/HAS realism candidate |
| fixed broadband reference | FCC MBA | reference only until conversion exists |
| real deployment metadata | Puffer | methodology and statistical caution |

## Generalization Rules

1. Do not tune on test traces.
2. Do not tune controller parameters after looking at OOD results.
3. Keep all split decisions in documentation before benchmark execution.
4. Separate route, day, user, session or source-domain splits when metadata allows.
5. Report when a dataset is methodology-only and not used as a trace input.
6. Treat different versions of a dataset as different provenance records.
7. Avoid claiming real-network generalization from a single emulator or synthetic suite.

## Reporting Requirements

Future reports must state:

- dataset IDs and versions;
- split policy;
- whether any parameter was tuned;
- whether OOD traces were inspected before final decisions;
- replay/emulation method used;
- limitations of the selected domains.

## Phase 3.2A Source-Triage Update

### Candidate Domain Ladder

1. Synthetic traces: runner/unit-test validation only, not final benchmark.
2. HSDPA Norway: legacy mobile, first integration candidate.
3. Ghent 4G/LTE: LTE mobile, first integration candidate.
4. Lancaster HAS: live/HAS/CDN throughput, broader benchmark-design candidate.
5. Raca 4G: modern mobile with KPIs, OOD candidate.
6. Raca 5G: modern 5G with KPIs and app patterns, OOD candidate.
7. Lumos5G: high-variance mmWave 5G, strong OOD candidate.
8. FCC: fixed broadband reference only until conversion plan.
9. Puffer: real-world methodology/data archive only until causal and storage plans exist.

### Claim Policy

- In-domain trace replay may support controlled comparison claims only within the selected trace domains.
- OOD claims require a dataset explicitly held out as OOD before any IA training or tuning.
- Real-world deployment claims are forbidden unless real-world deployment or a carefully justified equivalent is performed.
