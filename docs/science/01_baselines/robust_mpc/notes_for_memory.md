# robust_mpc Notes For Memory

## Neutral Academic Summary

The `robust_mpc` baseline extends MPC by making throughput prediction conservative when recent predictions have been inaccurate. It computes a base harmonic-mean prediction, estimates recent prediction error, reduces the prediction by the maximum recent error, and then runs the same MPC sequence search with the robust prediction.

## Citation Plan

Primary citations:

- Yin et al. 2015, `yin2015mpc`, for MPC structure and robust throughput correction.
- Mao et al. 2017, `mao2017pensieve`, only as historical neural/RL context and comparison source where RobustMPC appears as a strong classical baseline.

Do not cite this as a Pensieve implementation.

## Chapter 2 Contribution

Use RobustMPC to introduce robust hybrid ABR and the idea that throughput prediction error should influence future decisions. It should appear after MPC in the narrative.

## Chapter 5 Contribution

Use the implementation spec to document:

- reuse of MPC enumeration;
- harmonic mean base prediction;
- recent prediction-error window;
- robust prediction formula;
- fallback when history is insufficient;
- explicit exclusion of Pensieve/RL.

## Chapter 6 Contribution Later

After methodology exists, compare RobustMPC against MPC to test whether conservative prediction reduces risky selections in unstable conditions. Also use it as the strongest non-neural classical reference before any future AI/RL discussion.

## Suggested Table

RobustMPC correction table:

| variable | meaning |
| --- | --- |
| `base_prediction_Bps` | harmonic mean prediction |
| `error_i` | absolute percentage error for a past chunk |
| `err` | max recent error over window |
| `robust_prediction_Bps` | `base_prediction_Bps / (1 + err)` |

## Suggested Figure

Original diagram: actual throughput history + previous predictions -> error window -> robust throughput -> MPC horizon search -> first action.

## Limitations To Disclose

- RobustMPC is not Pensieve.
- No RL model, training, inference, ABR server, or dataset is created.
- Error alignment between prediction and later actual measurement must be implemented carefully.
- Internal objective weights are provisional and not final QoE.
- Segment sizes may be approximated as in MPC.

## Defense Message

RobustMPC is included because it is the natural strong classical baseline after MPC. It keeps the same planner but makes it less trusting of throughput estimates when recent prediction errors are large.
