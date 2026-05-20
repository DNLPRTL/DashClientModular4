# Method card — Linux tc/netem network emulation

## Identity

- Method/tool: Linux `tc netem`.
- Primary source: Linux manual page `tc-netem(8)`.
- Type: Linux queue discipline for network impairment emulation.
- Phase 3.2A status: mandatory method card.
- Phase 3.2A decision: fallback/alternative method candidate, not mandatory implementation.

## Problem solved

`tc netem` can emulate real-world network impairments such as delay, packet loss, duplication and corruption. It is useful for controlled Linux-only impairment experiments.

## What it emulates or replays

- Delay.
- Loss.
- Duplication.
- Corruption.
- Other qdisc/network impairment behavior depending on command options and kernel/iproute2 version.

## Inputs

- Linux network interface or namespace target.
- `tc` qdisc commands.
- Delay/loss/rate/corruption parameters.

## Outputs

- Network behavior modified by the configured qdisc.

## Platform requirements

- Linux/Ubuntu.
- `iproute2` tooling.
- Likely root/elevated privileges.
- Safe interface/namespace isolation required.

## Windows support

Not supported as a project path.

## Ubuntu support

Possible fallback or complement if the experiment needs simple impairment injection.

## Reproducibility and determinism

Lower than a pure Python fake/replay runner for unit tests because it depends on kernel, qdisc configuration, timing and privileges. It can still be useful in controlled runbooks.

## Required privileges

Likely elevated privileges. Must be documented before use.

## Integration risks

- Risk of modifying the wrong interface.
- Kernel/timer granularity affects behavior.
- Harder to include in default tests.
- Not a dataset converter or benchmark design by itself.

## Test strategy

- Do not implement in Phase 3.2A.
- If used later, isolate with network namespace or dedicated test interface.
- Use only after Python runner and artifact contract are stable.

## Why useful for DashClientModular4

It provides a lightweight Linux fallback if Mahimahi is too heavy or if simple delay/loss tests are needed.

## Why not enough alone

It does not ingest real throughput traces in a paper-grade way unless wrapped carefully, and it cannot replace dataset selection, replay runner artifacts or QoE decisions.

## Decision

`candidate-linux-fallback-no-implementation`

## Memory usage

- Chapter 5: possible emulation alternatives.
- Chapter 6: explain why it was not primary.

## BibTeX provisional

```bibtex
@manual{linuxTcNetemManual,
  title = {tc-netem(8) Linux manual page},
  organization = {Linux man-pages project},
  year = {2026},
  note = {Accessed 2026-05-20}
}
```
