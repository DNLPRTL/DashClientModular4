# mpc Notes For Memory

## Neutral Academic Summary

The `mpc` baseline is a hybrid ABR controller. It uses recent throughput measurements to predict future download capacity and buffer occupancy to simulate rebuffering risk over a short planning horizon. The controller applies the first action of the best-scoring sequence and repeats the process at the next segment.

## Citation Plan

Primary citation: Yin et al. 2015, `yin2015mpc`.

Use Bentaleb et al. 2019 for taxonomy if needed. Do not cite the internal controller objective as the TFG's final evaluation reward.

## Chapter 2 Contribution

Use MPC to introduce hybrid ABR methods that combine throughput prediction and buffer state. Contrast it with pure rate-based and pure buffer-based controllers.

## Chapter 5 Contribution

Use the implementation spec to document:

- harmonic mean throughput prediction;
- horizon enumeration;
- buffer evolution simulation;
- segment-size approximation;
- internal provisional objective;
- first-action receding-horizon behavior.

## Chapter 6 Contribution Later

After evaluation methodology exists, MPC can be compared with BBA/BOLA to test whether prediction plus buffer simulation improves behavior under controlled fake-engine conditions or later replay scenarios.

## Suggested Table

MPC parameter table:

| parameter | meaning |
| --- | --- |
| `horizon` | number of future chunks considered |
| `throughput_history_window` | recent samples used by predictor |
| `rebuffer_penalty` | internal cost per second of simulated rebuffering |
| `switch_penalty` | internal cost for quality variation |

## Suggested Figure

Original receding-horizon diagram: measure throughput -> predict -> enumerate sequences -> simulate buffer -> score -> apply first action.

## Limitations To Disclose

- The internal objective is provisional and not final QoE.
- Horizon `3` is a tractability choice, not exact paper equivalence.
- Segment sizes are approximated from bitrate and duration unless future data exists.
- No FastMPC table compression is implemented initially.
- No future throughput oracle, replay, or benchmark code is created here.

## Defense Message

MPC is the first baseline in the plan that reasons about the future. It is included because it combines the two main signals studied earlier: throughput and buffer occupancy.
