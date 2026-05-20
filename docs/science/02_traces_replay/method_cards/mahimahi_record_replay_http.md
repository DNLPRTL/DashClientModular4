# Method card — Mahimahi record-and-replay for HTTP

## Identity

- Method/tool: Mahimahi.
- Primary source: Ravi Netravali, Anirudh Sivaraman, Somak Das, Ameesh Goyal, Keith Winstein, James Mickens, Hari Balakrishnan. *Mahimahi: Accurate Record-and-Replay for HTTP*. USENIX ATC 2015.
- Type: HTTP record-and-replay and network emulation framework.
- Phase 3.2A status: mandatory method card.
- Phase 3.2A decision: candidate secondary validation path, not mandatory implementation.

## Problem solved

Mahimahi records HTTP-based application traffic and later replays the recorded traffic under controlled emulated network conditions. It is useful when the experiment needs a more realistic HTTP replay environment than a pure chunk-level simulator or a fake local runner.

## What it emulates or replays

- HTTP/HTTPS application traffic recorded from a client process.
- Fixed delay through DelayShell.
- Fixed-capacity and variable-capacity links through LinkShell.
- Time-varying links using packet-delivery traces.
- Multi-server web application behavior through separate local replay servers.

## Inputs

- Recorded HTTP traffic corpus.
- Delay configuration.
- Uplink/downlink link traces or packet-delivery opportunities.
- Client command executed inside Mahimahi shells.

## Outputs

- HTTP responses served from replayed local servers.
- Emulated network behavior observed by the client.
- Optional Mahimahi graphing/diagnostics depending on setup.

## Platform requirements

- Linux/Ubuntu path only for this project.
- Network namespaces and shell-based execution.
- Extra installation and environment work expected.

## Windows support

Not a primary Windows path for DashClientModular4. Windows should keep using unit-level/synthetic documentation validation and later the Python runner path.

## Ubuntu support

Candidate path. Any Mahimahi experiment must have a separate Ubuntu runbook and must not be required for baseline unit tests.

## Reproducibility and determinism

Potentially good when the same replay corpus, link traces and shell configuration are fixed. Integration still has more moving parts than a Python trace-driven runner, so Phase 3 should treat it as secondary validation, not the first implementation.

## Required privileges

TBD in project environment. Treat as requiring Linux networking setup and possible elevated privileges until verified.

## Integration risks

- Requires installation and platform-specific runbook.
- May not map cleanly to the exact DashClientModular4 traffic model without a dedicated test harness.
- Could slow progress if introduced before a simple trace schema and Python runner are validated.
- Must not become the source of benchmark claims before QoE/reward and run artifacts are closed.

## Test strategy

- Do not implement in Phase 3.2A.
- Later, test only after a custom trace schema and synthetic traces exist.
- Compare one or two simple traces against the Python runner to check whether delays/throughput constraints are qualitatively consistent.
- Keep Mahimahi tests out of default `unittest` unless a safe mockable wrapper exists.

## Why useful for DashClientModular4

Mahimahi is useful as a realism check for HTTP behavior and as a methodological bridge to prior ABR evaluation work that used network emulation.

## Why not enough alone

It does not decide dataset splits, QoE/reward, trace selection, statistical comparison, or causal validity. It also does not remove trace-driven simulation bias when observed traces were influenced by prior ABR decisions.

## Decision

`candidate-secondary-validation-path`

Primary Phase 3 implementation should remain a custom Python trace-driven fake/replay runner for reproducibility and unit-testability. Mahimahi can be studied and possibly used later on Ubuntu for selected validation runs.

## Memory usage

- Chapter 5: possible evaluation infrastructure.
- Chapter 6: comparison between controlled replay and emulation.
- Defense: justify why Mahimahi was considered but not made the first implementation target.

## BibTeX provisional

```bibtex
@inproceedings{netravali2015mahimahi,
  title = {Mahimahi: Accurate Record-and-Replay for HTTP},
  author = {Netravali, Ravi and Sivaraman, Anirudh and Das, Somak and Goyal, Ameesh and Winstein, Keith and Mickens, James and Balakrishnan, Hari},
  booktitle = {2015 USENIX Annual Technical Conference},
  year = {2015}
}
```
