# robust_mpc Notes For Memory

## Neutral Academic Summary

The `robust_mpc` baseline is the fifth academic ABR implementation after `rate_based`, `bba`, `bola`, and `mpc`. It extends MPC by making throughput prediction conservative when recent predictions have been inaccurate. It computes a base harmonic-mean prediction, estimates recent prediction error, reduces the prediction by the maximum recent error, and then runs the same MPC sequence search with the robust prediction.

## Citation Plan

Primary citations:

- Yin et al. 2015, `yin2015mpc`, for MPC structure and robust throughput correction.
- Mao et al. 2017, `mao2017pensieve`, only as historical neural/RL context and comparison source where RobustMPC appears as a strong classical baseline.

Do not cite this as a Pensieve implementation.

## Why RobustMPC Follows MPC

RobustMPC follows MPC because it keeps the same planner and changes only the trust placed in the throughput prediction. This is a clean scientific step:

- MPC: harmonic throughput prediction plus buffer simulation chooses the first action of the best sequence.
- RobustMPC: the same MPC planner uses a lower conservative throughput estimate when recent prediction error is high.

## Chapter 2 Contribution

Use RobustMPC to introduce robust hybrid ABR and the idea that throughput prediction error should influence future decisions. It should appear after MPC in the narrative.

## Chapter 5 Contribution

Use the implementation spec to document:

- reuse of MPC enumeration;
- harmonic mean base prediction;
- recent prediction-error window;
- robust prediction formula `base / (1 + max_error)`;
- startup fallback `base * startup_safety_factor`;
- state alignment between previous prediction and later actual throughput;
- explicit exclusion of Pensieve/RL.

## Chapter 6 Contribution Later

After methodology exists, compare RobustMPC against MPC to test whether conservative prediction reduces risky selections in unstable conditions. Also use it as the strongest non-neural classical reference before any future AI/RL discussion. Current fake smoke is integration validation only.

## Suggested Correction Table

| variable | meaning |
| --- | --- |
| `base_prediction_Bps` | harmonic mean prediction over recent actual throughput |
| `error_i` | absolute percentage error for a past chunk |
| `err` | max recent error over `prediction_error_window` |
| `robust_prediction_Bps` | `base_prediction_Bps / (1 + err)` |
| `startup_safety_factor` | fallback multiplier when no error history exists |

## Suggested Figure

Original diagram: actual throughput history + previous predictions -> error window -> robust throughput -> MPC horizon search -> first action.

## Limitations To Disclose

- RobustMPC is not Pensieve.
- No RL model, training, inference, ABR server, or dataset is created.
- Error alignment between prediction and later actual measurement is controller-local and bounded.
- Internal objective weights are provisional and not final QoE.
- Segment sizes may be approximated as in MPC.
- Smoke results are integration validation, not benchmark evidence.

## Defense Message

RobustMPC is included because it is the natural strong classical baseline after MPC. It keeps the same planner but makes it less trusting of throughput estimates when recent prediction errors are large. The tests prove robustness behavior by checking zero-error equivalence, high-error conservatism, fallback correction, safe zero-throughput handling, bounded error windows, first-action behavior, no Pensieve/RL dependency and forbidden-signal independence.
