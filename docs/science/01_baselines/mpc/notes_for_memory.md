# mpc Notes For Memory

## Neutral Academic Summary

The `mpc` baseline is the fourth academic ABR implementation after `rate_based`, `bba`, and `bola`. It is a hybrid controller: recent application-layer throughput measurements provide a capacity prediction, and buffer occupancy is used to simulate rebuffering risk over a short planning horizon. The controller applies the first action of the best-scoring sequence and repeats the process at the next segment.

## Citation Plan

Primary citation: Yin et al. 2015, `yin2015mpc`.

Use Bentaleb et al. 2019 for taxonomy if needed. Do not cite the internal controller objective as the TFG's final evaluation reward.

## Why MPC Follows BOLA

BBA and BOLA validated buffer-driven baselines first. MPC follows them because it adds prediction and planning on top of the already tested buffer signal instead of replacing the controller contract. This gives the thesis a clear progression:

- `rate_based`: throughput estimate drives the decision.
- `bba`: buffer level drives a reservoir/cushion map.
- `bola`: buffer and utility/size enter a Lyapunov-style score.
- `mpc`: throughput prediction and buffer simulation score future action sequences.

## Chapter 2 Contribution

Use MPC to introduce hybrid ABR methods that combine throughput prediction and buffer state. Contrast it with pure rate-based and pure buffer-based controllers.

## Chapter 5 Contribution

Use the implementation spec to document:

- harmonic mean throughput prediction over recent positive samples;
- horizon enumeration with default horizon `3`;
- buffer evolution simulation;
- segment-size approximation as `rate * fragment_duration` when exact sizes are absent;
- exact segment-size handling when per-level sizes are supplied;
- internal provisional objective;
- first-action receding-horizon behavior.

## Chapter 6 Contribution Later

After evaluation methodology exists, MPC can be compared with BBA/BOLA under controlled scenarios or later replay support. Current fake smoke is integration validation only.

## Suggested Parameter Table

| parameter | meaning |
| --- | --- |
| `horizon` | number of future chunks considered; default `3` |
| `throughput_history_window` | recent positive samples used by harmonic mean; default `5` |
| `rebuffer_penalty` | internal cost per second of simulated rebuffering; default `4.3` |
| `switch_penalty` | internal cost for quality variation; default `1.0` |
| `max_enumerated_sequences` | cap that reduces effective horizon when needed; default `4096` |

## Suggested Figure

Original receding-horizon diagram: measure throughput -> predict -> enumerate sequences -> simulate buffer -> score -> apply first action.

## Limitations To Disclose

- The internal objective is provisional and not final QoE.
- Horizon `3` is a tractability choice, not exact paper equivalence.
- Segment sizes are approximated from bitrate and duration unless exact per-level data exists.
- No FastMPC table compression is implemented initially.
- No future throughput oracle, replay, or benchmark code is created here.
- RobustMPC is deferred to the next implementation block.

## Defense Message

MPC is the first implemented academic baseline in this sequence that plans over future chunks. It is included because it combines the two main signals validated earlier: throughput and buffer occupancy. The tests prove the decision rule by checking harmonic prediction, buffer simulation, rebuffer and switching penalties, first-action behavior, deterministic enumeration, edge-case fallback, and forbidden-signal invariants.
