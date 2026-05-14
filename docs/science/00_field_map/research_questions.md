# Research Questions

## Main Question

How can a modular MPEG-DASH client be extended with classic ABR baselines in a scientifically traceable way while preserving reproducibility and separating runtime behavior from evaluation methodology?

## Supporting Questions

| id | question | linked docs |
| --- | --- | --- |
| RQ1 | Which ABR baseline families are appropriate for an initial TFG comparison before AI/RL work? | `../01_baselines/baseline_selection_matrix.md` |
| RQ2 | Which client signals are required by each selected baseline, and which are already available or derivable? | `../01_baselines/baseline_signal_matrix.md` |
| RQ3 | What documentation must exist before translating a paper into code? | `../01_baselines/*_template.md` |
| RQ4 | How should DASH terminology be grounded without copying standard text into the repository or thesis? | `dash_standard_reference.md` |
| RQ5 | How can local UGR-related streaming traffic work motivate the problem without creating runtime requirements? | `local_streaming_related_work.md` |
| RQ6 | Which limitations must be declared before evaluation begins? | `../07_memory/rubric_alignment.md` and `../07_memory/originality_and_citation_policy.md` |

## Deferred Questions

- What is the final QoE/reward formula?
- Which trace datasets or replay mechanisms will be used?
- How will real playback and fake-engine results be separated in the final evaluation?
- Whether a modern optional controller such as SODA is worth adding after the mandatory baselines.
- Whether an AI/RL controller is appropriate after Phase 2.
