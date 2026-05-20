# Phase 2 Defense Talking Points

## Why These Baselines Were Selected

The selected set covers the main non-neural ABR families needed before IA work: throughput-based (`rate_based`), buffer-based (`bba`), utility/buffer (`bola`), planning (`mpc`) and robust planning (`robust_mpc`). This creates a balanced baseline floor without turning Phase 2 into a full survey implementation project.

## Why Sanity Controllers Came First

`min_rate`, `fixed_rate` and `max_rate` are not academic baselines. They validate the controller registry, units, representation quantization, fake-engine path and artifact production before more complex algorithms are trusted.

## How Paper Evidence Became Code

The workflow is:

```text
paper/source evidence -> implementation spec -> controller API mapping -> acceptance tests -> code -> unit tests -> fake smoke -> memory notes
```

This prevents direct coding from raw PDFs and makes each implementation defensible in the memory and defense.

## Why Codex Did Not Decide The Science

Codex assisted with implementation and documentation, but the scientific decisions are recorded in local source cards, selection matrices, specs, acceptance tests and limitation documents. The project defends documented methodology, not an opaque assistant preference.

## Why Fake Smoke Is Not Benchmark

Fake smoke proves the client can instantiate a controller, run the loop, produce feedback, select rates and write canonical artifacts. It does not reproduce real networks, does not compare QoE, does not rank algorithms and does not validate final reward.

## Why Final QoE And Replay Come Later

QoE/reward and replay/traces affect the meaning of results. Defining them after controller implementation avoids mixing baseline construction with evaluation claims. Phase 3 must establish reproducible network conditions first.

## Why This Is A Strong Basis For IA Later

IA/RL controllers need:

- stable non-neural baselines;
- a reproducible client;
- a clear controller contract;
- trace/replay methodology;
- leakage controls;
- final reward definitions.

Phase 2 provides the first three and explicitly defers the rest so the future IA phase can be scientifically comparable.

## Common Questions

| question | concise answer |
| --- | --- |
| Did Phase 2 prove RobustMPC is best? | No. It proved the implementation is present, tested and bounded. Ranking waits for evaluation methodology. |
| Is BOLA the same as dash.js production behavior? | No. It is BOLA-basic. DYNAMIC and FAST SWITCHING are deferred. |
| Is RobustMPC Pensieve? | No. Pensieve is an IA/RL reference. RobustMPC here is a classical robust MPC variant. |
| Why no SODA? | SODA is documented as a modern optional candidate, but it is outside the mandatory Phase 2 set. |
| Why no replay yet? | Replay/emulation is Phase 3 because it defines the experimental environment, not the baseline implementation itself. |
