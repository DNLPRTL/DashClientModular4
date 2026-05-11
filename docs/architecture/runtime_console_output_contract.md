# Runtime Console Output Contract

Date: 2026-05-11

Runtime console output, progress bars, and small operator windows are human-facing diagnostics. They are not canonical benchmark output and must not be parsed by benchmark scripts.

## Canonical Data Artifacts

The canonical run artifacts are:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `segment_telemetry.csv`
- `evaluation_segments.csv`
- `run.log`

`segment_telemetry.csv` and `evaluation_segments.csv` are validation/evaluation artifacts, not final benchmark result tables. Console/progress text is less authoritative than those artifacts and the resolved config/manifest.

## Progress And Status Labels

Progress bars and status lines must avoid introducing academic terminology before methodology exists. Human labels should describe what the runtime currently knows without implying final QoE, reward, baseline, or benchmark semantics.

Avoid ambiguous labels such as `BW` unless they are explicitly defined in the same UI. Preferred labels are:

- target rate;
- measured download rate;
- throughput estimate;
- representation rate;
- selected level;
- buffer estimate;
- eval phase.

The legacy controller feedback key `bwe` may still appear in developer-facing traces because it is part of the current controller contract. Human-facing UI should explain it as a measured download-rate/fallback signal, not as final bandwidth estimation methodology.

## Current Legacy Terminology Classification

- `bwe`: current controller-contract key; deprecated/legacy alias for a measured download-rate fallback value. It is not final bandwidth methodology.
- `cur_bitrate`, `max_bitrate`, `min_bitrate`: legacy feedback names whose values are bytes per second, not bits per second.
- `phase_raw` and `phase_smooth`: runtime/debug phase detector labels, not benchmark authority.
- `stall_flag` and `stall_duration`: segment-level runtime aggregates, not final QoE rebuffer events.
- `Visible:`: not emitted by the current runtime audit. If it appears in future debug output, treat it as a non-canonical integration/display diagnostic.
- Spanish or debug strings in console output: acceptable for local diagnostics, but non-canonical.

## Rules

- Console output may be localized, shortened, or cleaned later without changing benchmark data.
- Benchmark scripts must read canonical artifacts, not terminal rendering, Tk labels, ANSI output, or progress-window text.
- Console labels must not claim that a run is a benchmark, a final QoE result, a training dataset, or a validated academic comparison.
- Runtime text cleanup must be text-only unless a separate block explicitly changes behavior.
- Text cleanup must not change data values, loop timing, playback semantics, ABR decisions, downloader behavior, parser behavior, or media-engine behavior.
- GStreamer output must state or preserve the caveat that GStreamer is integration/demo in Phase 1, not benchmark-grade.
