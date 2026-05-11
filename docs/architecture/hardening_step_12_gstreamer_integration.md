# Hardening Step 12: GStreamer Integration

This block hardens GStreamer as an integration/demo path. It does not make GStreamer benchmark-grade.

## What Changed

- Improved the unavailable GStreamer/PyGObject error so it points to `media_engine.name: fake`, Windows expectations, and the strict Ubuntu GST environment check.
- Replaced raw pipeline assertion failure with explicit `RuntimeError` diagnostics.
- Added required-element checks for `appsrc`, `qtdemux`, `h264parse`, `queue`, `avdec_h264` when decoding is enabled, and the selected sink.
- Stopped silently falling back to `fakesink` when the user explicitly selects a sink that cannot be created.
- Logged concise startup diagnostics for `decode_video`, `sink_name`, visible playback, and `min_queue_time`.
- Included bus error source information in emitted engine error events.
- Made `stop()` safer to call repeatedly and during partial startup failure.
- Added unit tests using mocks so Windows and CI-like local tests do not require real GStreamer, a display server, network, or a DASH server.
- Added a dedicated GStreamer playback runbook.

## What Did Not Change

This block does not implement baselines, IA, PPO, QoE, reward, trace infrastructure, benchmark scripts, or benchmark methodology.

It does not change the fake-engine benchmark role. The fake media engine remains the controlled deterministic path for tests, replay, and future benchmark work.

It does not change controller decisions, runtime feedback semantics, CSV semantics, downloader behavior, parser behavior, or fake-engine behavior.

GStreamer output must not be mixed with fake-engine output as equivalent benchmark data. `segment_telemetry.csv` and `evaluation_segments.csv` remain validation/control artifacts, not final benchmark results.
