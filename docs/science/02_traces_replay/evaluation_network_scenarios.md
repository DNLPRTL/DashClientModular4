# Evaluation Network Scenarios

This document names future network scenarios. It does not define final QoE/reward and does not run benchmarks.

## Scenario Families

| id | scenario | purpose | possible source |
| --- | --- | --- | --- |
| SC-STABLE-BROADBAND | stable high-throughput path | Sanity reference for low-stress adaptation. | synthetic trace first; FCC only as reference until converted |
| SC-CONSTRAINED | throughput below top representation | Check conservative selection and buffer pressure. | synthetic trace first |
| SC-STEP-DROP | sudden capacity drop | Check reaction to worsening conditions. | synthetic trace, HSDPA/4G candidates later |
| SC-STEP-RECOVERY | sudden capacity recovery | Check upgrade behavior after recovery. | synthetic trace, HSDPA/4G candidates later |
| SC-OSCILLATORY | recurring capacity swings | Check oscillation sensitivity. | synthetic trace, mobile candidates later |
| SC-BLIPS | short outages or severe dips | Check robustness around stalls without defining final QoE. | synthetic trace first |
| SC-LEGACY-MOBILE | commute-style 3G/HSDPA | Classic mobile ABR evaluation setting. | Norway HSDPA |
| SC-MODERN-MOBILE | 4G/5G mobile variation | OOD/generalization pressure. | Ghent 4G, Raca 4G/5G, Lumos5G |
| SC-LIVE-HAS | CDN/live-derived throughput | Live/HAS realism. | Lancaster ABR traces |

## Scenario Rules

- Start with synthetic traces before any real dataset conversion.
- Keep each scenario source and trace ID explicit.
- Use the same scenario list for all controllers under comparison.
- Do not change controller parameters per scenario unless a later protocol explicitly allows it.
- Do not call scenario runs final benchmarks until QoE/reward and result interpretation are closed.

## Deferred Design Decisions

- final number of traces per scenario;
- final segment duration assumptions;
- final startup buffer assumptions;
- final QoE/reward;
- final aggregation and confidence interval policy;
- final GStreamer role, if any.

