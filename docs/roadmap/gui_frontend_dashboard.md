# GUI / Operator Dashboard Roadmap

Date: 2026-05-11

This is a roadmap document only. It registers a future UI block and does not implement a GUI.

## Future UI Block

Future block: GUI / operator dashboard / VLC-like frontend.

The UI should be a demo/operator layer over the same config, run context, controller contracts, media-engine choices, and run artifacts used by the CLI. It must not become benchmark authority.

## Scope

The future GUI may provide:

- MPD URL selection;
- controller selection;
- media engine selection: `fake` or `gst`;
- headless/visible playback selection;
- editing of safe config fields;
- run launch;
- live human-readable progress;
- selected level display;
- target rate display;
- measured download rate display;
- buffer estimate display;
- eval phase display;
- stalls/events display;
- opening run directories;
- visualization of `segment_telemetry.csv` after a run;
- visualization of `evaluation_segments.csv` after a run;
- graphs for throughput, selected level, buffer, stalls, and eval phases;
- later run comparison, only after benchmark methodology is defined.

## Hard Boundaries

- The GUI is not benchmark authority.
- CLI/config/run artifacts remain canonical for experiments.
- The GUI must consume the same config, `run_context`, controller contract, telemetry schema, and artifact contracts as the CLI.
- The GUI must not hide stalls or rewrite results.
- The GUI must not silently mix fake and GStreamer runs as equivalent benchmark data.
- The GUI must not train AI.
- The GUI must not define final QoE or reward.
- The GUI must not introduce ABR baselines before Phase 0 methodology and Phase 2 implementation decisions.
- GUI implementation should happen after Phase 1 closure and methodology decisions, or as a separate demo layer that does not contaminate benchmark work.

## Recommended Timing

Implement this only after Phase 1 acceptance and after the next methodology decisions clarify what must remain canonical in CLI/config/artifacts. If built earlier for demonstration, keep it explicitly separate from benchmark scripts and academic result generation.
