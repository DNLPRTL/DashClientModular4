# Source Inventory

| id | type | title | authors | year | venue | DOI/URL | priority | target_folder | use_in_TFG | use_in_memory | provisional_bibtex_key | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FM-01 | DASH background | Dynamic Adaptive Streaming over HTTP: Standards and Design Principles | Thomas Stockhammer | 2011 | ACM MMSys | https://doi.org/10.1145/1943552.1943572 | P0 | `00_field_map/paper_cards/` | DASH design background: MPD, segments, HTTP, client-driven adaptation | Chapter 2 background | `stockhammer2011dash` | card created |
| FM-02 | standard | ISO/IEC 23009-1:2022, MPEG-DASH Part 1 | ISO/IEC JTC 1/SC 29 | 2022 | International Standard | https://www.iso.org/standard/83314.html | P0 | `00_field_map/` | Official terminology reference only | Chapter 2 terminology and bibliography | `iso23009_1_2022` | reference note created |
| FM-03 | survey | A Survey on Bitrate Adaptation Schemes for Streaming Media Over HTTP | Abdelhak Bentaleb, Bayan Taani, Ali C. Begen, Christian Timmerer, Roger Zimmermann | 2019 | IEEE Communications Surveys & Tutorials | https://doi.org/10.1109/COMST.2018.2862938 | P0 | `00_field_map/paper_cards/` | Main ABR taxonomy and signal map | Chapters 2 and 6 | `bentaleb2019survey` | card created |
| FM-04 | review | HTTP Adaptive Streaming: A Review on Current Advances and Future Challenges | Christian Timmerer, Hadi Amirpour, Farzad Tashtarian, Samira Afzal, Amr Rizk, Michael Zink, Hermann Hellwagner | 2025 | ACM TOMM | https://doi.org/10.1145/3736306 | P1 | `00_field_map/paper_cards/` | Recent HAS review and future directions | Chapters 1 and 2 | `timmerer2025hasReview` | card created |
| FM-05 | survey/tutorial | An End-to-End Pipeline Perspective on Video Streaming in Best-Effort Networks: A Survey and Tutorial | Leonardo Peroni, Sergey Gorinsky | 2025 | ACM Computing Surveys | https://doi.org/10.1145/3742472 | P1 | `00_field_map/paper_cards/` | End-to-end pipeline context from ingestion to playback | Chapters 1, 2, and 6 | `peroni2025pipelineSurvey` | card created |
| FM-06 | local related work | Analysis and modelling of YouTube traffic | Pablo Ameigeiras, Juan J. Ramos-Munoz, Jorge Navarro-Ortiz, Juan M. Lopez-Soler | 2012 | Transactions on Emerging Telecommunications Technologies | https://doi.org/10.1002/ett.2546 | P1 | `00_field_map/paper_cards/` | Local UGR traffic characterization, progressive download, burst/throttling | Chapters 1 and 2 | `ameigeiras2012youtubeTraffic` | card created |
| FM-07 | local related work | Characteristics of mobile YouTube traffic | Juan J. Ramos-Munoz, Jonathan Prados-Garzon, Pablo Ameigeiras, Jorge Navarro-Ortiz, Juan M. Lopez-Soler | 2014 | IEEE Wireless Communications | https://doi.org/10.1109/MWC.2014.6757893 | P1 | `00_field_map/paper_cards/` | Local UGR mobile traffic characterization | Chapters 1 and 2 | `ramosMunoz2014mobileYoutube` | card created |

## Inventory Rules

- `P0` sources are mandatory for terminology, taxonomy, or initial baseline justification.
- `P1` sources strengthen positioning and recent context.
- A source inventory entry does not authorize code implementation.
- Any future source added here must receive a source card before it is used in design or implementation.
