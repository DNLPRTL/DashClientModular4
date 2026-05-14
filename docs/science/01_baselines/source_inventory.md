# Baseline Source Inventory

| id | type | title | authors | year | venue | DOI/URL | priority | target_folder | use_in_TFG | use_in_memory | provisional_bibtex_key | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BS-01 | baseline paper | Rate Adaptation for Adaptive HTTP Streaming | Changhao Liu, Imed Bouazizi, Moncef Gabbouj | 2011 | ACM MMSys | https://doi.org/10.1145/1943552.1943575 | P0 | `rate_based/` | Mandatory throughput/rate-based baseline | Chapters 2, 5, 6 | `liu2011rateAdaptation` | paper card created |
| BS-02 | baseline paper | A Buffer-Based Approach to Rate Adaptation: Evidence from a Large Video Streaming Service | Te-Yuan Huang, Ramesh Johari, Nick McKeown, Matthew Trunnell, Mark Watson | 2014 | ACM SIGCOMM | https://doi.org/10.1145/2619239.2626296 | P0 | `bba/` | Mandatory BBA baseline | Chapters 2, 5, 6 | `huang2014bba` | paper card created |
| BS-03 | baseline paper | BOLA: Near-Optimal Bitrate Adaptation for Online Videos | Kevin Spiteri, Rahul Urgaonkar, Ramesh K. Sitaraman | 2020 | IEEE/ACM Transactions on Networking | https://doi.org/10.1109/TNET.2020.2996964 | P0 | `bola/` | Mandatory BOLA baseline | Chapters 2, 5, 6 | `spiteri2020bola` | paper card created |
| BS-04 | baseline paper | A Control-Theoretic Approach for Dynamic Adaptive Video Streaming over HTTP | Xiaoqi Yin, Abhishek Jindal, Vyas Sekar, Bruno Sinopoli | 2015 | ACM SIGCOMM | https://doi.org/10.1145/2785956.2787486 | P0 | `mpc/` and `robust_mpc/` | Mandatory MPC source and RobustMPC base | Chapters 2, 5, 6 | `yin2015mpc` | paper card created |
| BS-05 | neural/RL reference | Neural Adaptive Video Streaming with Pensieve | Hongzi Mao, Ravi Netravali, Mohammad Alizadeh | 2017 | ACM SIGCOMM | https://doi.org/10.1145/3098822.3098843 | P1 | `robust_mpc/` | Historical neural reference and RobustMPC comparison source | Chapters 2 and limitations | `mao2017pensieve` | source artifact card created |
| BS-06 | practical source | From Theory to Practice: Improving Bitrate Adaptation in the DASH Reference Player | Kevin Spiteri, Ramesh K. Sitaraman, Daniel Sparacio | 2019 | ACM TOMM | https://doi.org/10.1145/3336497 | P1 | `bola/` | Practical dash.js source for BOLA-E, DYNAMIC, FAST SWITCHING, and Sabre | Chapters 2 and 5 notes | `spiteri2019dashjs` | source card created |
| BS-07 | optional candidate paper | SODA: An Adaptive Bitrate Controller for Consistent High-Quality Video Streaming | Tianyu Chen, Yiheng Lin, Nicolas Christianson, Zahaib Akhtar, Sharath Dharmaji, Mohammad Hajiesmaili, Adam Wierman, Ramesh K. Sitaraman | 2024 | ACM SIGCOMM | https://doi.org/10.1145/3651890.3672260 | P2 | `optional_methods/soda/` | Strong modern non-neural optional candidate | Future work/annex only unless selected later | `chen2024soda` | candidate card created |

## Source Rules

- `P0` sources are mandatory for the initial academic baseline set.
- `P1` sources support comparison, practical context, or historical framing.
- `P2` sources are optional and must not enter the initial implementation order.
- A source inventory row is not an implementation authorization.
