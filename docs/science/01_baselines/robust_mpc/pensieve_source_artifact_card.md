# Source Artifact Card: Pensieve and RobustMPC

| field | value |
| --- | --- |
| title | Neural Adaptive Video Streaming with Pensieve |
| authors | Hongzi Mao, Ravi Netravali, Mohammad Alizadeh |
| year | 2017 |
| venue | ACM SIGCOMM 2017 |
| DOI/URL if known | https://doi.org/10.1145/3098822.3098843; project page: https://web.mit.edu/pensieve/ |
| type | Neural/RL reference and comparison artifact |
| role in the TFG | Historical neural ABR reference and practical source for how RobustMPC is described/comparable in Pensieve-style evaluations. |
| key contribution | Shows a reinforcement-learning approach to ABR and compares it with classic baselines including RobustMPC. |
| algorithm family if applicable | Neural/RL ABR; RobustMPC comparison source. |
| required signals if applicable | For Pensieve: state vector, QoE reward, trained model, traces/simulator. For RobustMPC reference: prediction error history and MPC inputs. |
| implementation relevance | Use only to document RobustMPC comparison semantics and the past-5-chunk prediction-error normalization note. |
| what it does NOT justify | Does not justify implementing Pensieve, training models, creating RL datasets, defining final reward, or adding an AI controller in Phase 2. |
| use in thesis memory | Chapter 2 neural ABR history and Chapter 6 limitations/future work. |
| provisional BibTeX key | `mao2017pensieve` |
| decision | Source artifact only for this block; do not implement Pensieve. |

## RobustMPC Note

RobustMPC should be documented as using the same general MPC approach while adjusting throughput estimates according to recent prediction errors. The exact formula must be specified in `implementation_spec.md` before any code is written.
