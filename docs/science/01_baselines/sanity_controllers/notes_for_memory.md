# Sanity Controllers Notes For Memory

## Thesis Use

Sanity controllers should be described in Chapter 5 as validation tools for the controller interface. They should not be included in scientific baseline rankings.

## Suggested Wording

The `min_rate`, `fixed_rate`, and `max_rate` controllers are deterministic controls used to validate the ABR integration path. They provide lower, fixed, and upper ladder behavior checks before paper-derived controllers are added.

## Implementation Notes

- Code module: `core/controller/sanity_rate.py`.
- Registry names: `min_rate`, `fixed_rate`, `max_rate`.
- Existing debug/legacy names `fixed_quality`, `scripted_quality`, and `max_quality` remain available.
- Target rates are bytes per second.
- Quality levels are representation indices.
- The fake engine validates integration and artifacts, not final benchmark performance.

## Limitations

- No academic ABR claim.
- No QoE optimization claim.
- No comparison against literature baselines.
- Fake-engine validation only until the evaluation methodology is defined.
