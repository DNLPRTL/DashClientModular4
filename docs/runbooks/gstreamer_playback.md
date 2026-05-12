# GStreamer Playback

GStreamer is an integration/demo playback path for Phase 1. It is useful for validating that the client can feed a real media pipeline on Ubuntu, but it is not the primary benchmark path and is not benchmark-grade yet.

Block 14 readiness keeps this boundary: GStreamer is useful for integration evidence, not final timing/QoE authority.

The fake media engine remains preferred for deterministic tests, replay, and future benchmark/control work. Do not compare fake-engine and GStreamer outputs as equivalent benchmark results.

Visible playback proves integration/demo behavior on one prepared machine. It does not prove academic benchmark validity.

Windows does not need GStreamer. Windows validation should keep using unit tests, fake-engine smoke tests, and non-strict GST environment checks.

## Ubuntu Capability Check

On the Ubuntu client VM, GStreamer validation should first pass:

```bash
python scripts/check_environment.py --profile gst --strict
```

If this fails, fix the Ubuntu GStreamer/PyGObject installation before running with `media_engine.name: "gst"`.

## Headless GST Run

For headless validation, keep decoding disabled and let the engine select `fakesink`:

```yaml
media_engine:
  name: "gst"
  min_queue_time: 1.0
  decode_video: false
  sink_name: null
```

With `decode_video: false` and no explicit `sink_name`, the engine uses `fakesink`. This is the safest GST path for SSH sessions and automated-looking manual checks.

This mode is structural validation only. `fakesink`/headless operation may not enforce real-time visible playback and can complete faster than real time. Timing and QoE derived from this mode are not benchmark-grade.

## Optional Visible Playback

Visible playback is optional and requires a working display server:

```yaml
media_engine:
  name: "gst"
  min_queue_time: 1.0
  decode_video: true
  sink_name: "autovideosink"
```

Other sinks can be selected explicitly, for example `xvimagesink`, `glimagesink`, or `waylandsink`, depending on the machine. If an explicit sink cannot be created, the run fails clearly instead of silently falling back to `fakesink`.

Visible playback can fail on headless SSH, missing `DISPLAY`, missing Wayland/X11 access, or missing sink plugins. That is an integration environment failure, not a benchmark failure.

Visible playback is optional demo validation. It can confirm that decoding and rendering work on the Ubuntu client, but it is still not a benchmark-grade timing path.

## Diagnostics

The GST engine logs the selected mode at startup:

- `decode_video`
- selected `sink_name`
- whether the sink was explicit
- whether visible playback is requested
- `min_queue_time`

Missing required elements are reported by element name, such as `appsrc`, `qtdemux`, `h264parse`, `queue`, `avdec_h264`, or the selected sink.

When GStreamer or PyGObject is unavailable, the client points back to `media_engine.name: fake` and the strict Ubuntu environment check.

## Output Interpretation

`segment_telemetry.csv` and `evaluation_segments.csv` remain validation/evaluation artifacts, not final QoE results. Rows with `use_for_eval=false` are not benchmark rows. Terminal drain stalls are still not steady-state rebuffering.

No final QoE/reward, IA training dataset, academic baseline comparison, or GStreamer benchmark methodology exists yet.

Do not compare fake and GST run outputs as equivalent benchmark runs. The fake engine remains the controlled path for deterministic tests, replay-oriented development, and future benchmark/control work.
