# bba Notes For Memory

## Neutral Academic Summary

The `bba` baseline represents buffer-based ABR. It maps playback buffer occupancy to a representation through a reservoir and cushion: low buffer selects the minimum rate, high buffer selects the maximum rate, and the intermediate region maps deterministically across the bitrate ladder.

## Citation Plan

Primary citation: Huang et al. 2014, `huang2014bba`.

Use Bentaleb et al. 2019 for taxonomy if needed. Do not cite the implementation as Netflix production behavior.

## Chapter 2 Contribution

Use BBA to explain the buffer-based design philosophy: buffer level can summarize previous network behavior and can drive bitrate selection without a continuous bandwidth predictor.

## Chapter 5 Contribution

Use the implementation spec to document:

- `queued_time` as `buffer_level_s`;
- `reservoir_s` and `cushion_s`;
- deterministic discrete mapping to the MPD ladder;
- fallback to minimum rate on invalid buffer;
- no throughput dependency for BBA-0.

## Chapter 6 Contribution Later

After methodology exists, BBA can be compared against rate-based controllers to show the contrast between capacity-driven and buffer-driven adaptation. It should also be compared with BOLA to distinguish hand-designed buffer maps from utility-based buffer optimization.

## Suggested Table

Buffer threshold table:

| buffer region | expected decision |
| --- | --- |
| `buffer <= reservoir_s` | minimum representation |
| `reservoir_s < buffer < reservoir_s + cushion_s` | intermediate ladder mapping |
| `buffer >= reservoir_s + cushion_s` | maximum representation |

## Suggested Figure

Original reservoir/cushion diagram with buffer on the x-axis and selected representation on the y-axis. Do not copy paper figures.

## Limitations To Disclose

- This is BBA-0-style, not Netflix production internals.
- Reservoir and cushion defaults are configurable experimental choices.
- Startup throughput guard is deferred.
- VBR-specific behavior is not implemented initially.
- No final QoE/reward is defined here.

## Defense Message

BBA is included because it is the cleanest contrast to throughput-driven ABR: it makes the buffer the central state variable and keeps the initial controller simple enough to verify deterministically.
