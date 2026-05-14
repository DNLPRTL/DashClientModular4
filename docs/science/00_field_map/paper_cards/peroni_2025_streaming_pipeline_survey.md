# Source Card: Peroni and Gorinsky 2025 Pipeline Survey

| field | value |
| --- | --- |
| title | An End-to-End Pipeline Perspective on Video Streaming in Best-Effort Networks: A Survey and Tutorial |
| authors | Leonardo Peroni, Sergey Gorinsky |
| year | 2025 |
| venue | ACM Computing Surveys |
| DOI/URL if known | https://doi.org/10.1145/3742472 |
| type | End-to-end video streaming survey/tutorial |
| role in the TFG | Provide pipeline context from ingestion and processing to distribution, ABR, CDN support, playback, and QoE. |
| key contribution | Frames streaming as a full pipeline rather than only a player-side controller problem. |
| algorithm family if applicable | Survey/tutorial across intuition-based, theory-based, and learning-based methods. |
| required signals if applicable | Not a single controller; useful for mapping pipeline signals and evaluation dimensions. |
| implementation relevance | Reinforces why this TFG narrows scope to client-side ABR while documenting broader system boundaries. |
| what it does NOT justify | Does not require implementing CDN, encoding, trace replay, or AI components. |
| use in thesis memory | Chapters 1, 2, and evaluation limitations in Chapter 6. |
| provisional BibTeX key | `peroni2025pipelineSurvey` |
| decision | Cite as recent end-to-end context; keep implementation scope client-side. |
