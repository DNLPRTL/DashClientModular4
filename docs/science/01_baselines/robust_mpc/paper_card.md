# Paper Card: RobustMPC Baseline

| field | value |
| --- | --- |
| title | RobustMPC baseline derived from MPC and documented through Pensieve comparisons |
| authors | Xiaoqi Yin, Abhishek Jindal, Vyas Sekar, Bruno Sinopoli; Hongzi Mao, Ravi Netravali, Mohammad Alizadeh |
| year | 2015 / 2017 |
| venue | ACM SIGCOMM 2015 / ACM SIGCOMM 2017 |
| DOI/URL if known | MPC: https://doi.org/10.1145/2785956.2787486; Pensieve: https://doi.org/10.1145/3098822.3098843 |
| type | Academic baseline card with source-artifact dependency |
| role in the TFG | Mandatory robust variant after MPC, using MPC as the base and Pensieve as the comparison/source artifact for robust prediction handling. |
| key contribution | Uses the MPC approach while accounting for prediction errors by normalizing throughput estimates using the maximum error observed in the past 5 chunks. |
| algorithm family if applicable | Robust model predictive control. |
| required signals if applicable | MPC signals plus recent throughput prediction error history, especially a 5-chunk error window. |
| implementation relevance | Future implementation should be layered after MPC and must document how prediction error is computed and applied. |
| what it does NOT justify | Does not justify implementing Pensieve, training RL models, or adding AI infrastructure in Phase 2. |
| use in thesis memory | Chapter 2 robust MPC context; Chapter 5 implementation; Chapter 6 comparison against MPC. |
| provisional BibTeX key | `yin2015mpc` and `mao2017pensieve` |
| decision | Mandatory later baseline after MPC; implementation blocked until full docs and QoE dependency are resolved. |
