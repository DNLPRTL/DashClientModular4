# Paper Card: MPC Baseline

| field | value |
| --- | --- |
| title | A Control-Theoretic Approach for Dynamic Adaptive Video Streaming over HTTP |
| authors | Xiaoqi Yin, Abhishek Jindal, Vyas Sekar, Bruno Sinopoli |
| year | 2015 |
| venue | ACM SIGCOMM 2015 |
| DOI/URL if known | https://doi.org/10.1145/2785956.2787486 |
| type | Academic ABR baseline paper |
| role in the TFG | Primary source for the mandatory MPC baseline and base source for RobustMPC. |
| key contribution | Uses model predictive control to combine throughput prediction and buffer occupancy over a future horizon to optimize QoE. |
| algorithm family if applicable | Model predictive control / QoE optimization. |
| required signals if applicable | Throughput history, throughput prediction, buffer occupancy, representation ladder, segment duration/size model, horizon, and QoE weights. |
| implementation relevance | Implemented in Phase 2.3.5 as enumerative MPC with harmonic throughput prediction, buffer simulation, segment-size modeling and an internal provisional objective. |
| what it does NOT justify | Does not justify treating the controller-internal objective as final QoE/reward. Does not justify FastMPC, RobustMPC, benchmark scoring or AI/RL work in this block. |
| use in thesis memory | Chapter 2 MPC background; Chapter 5 implementation; Chapter 6 comparison and limitations. |
| provisional BibTeX key | `yin2015mpc` |
| decision | Mandatory baseline implemented as the fourth academic ABR controller; RobustMPC remains deferred. |
