# DASH Standard Reference

## Reference

| field | value |
| --- | --- |
| Standard | ISO/IEC 23009-1:2022 |
| Title | Information technology - Dynamic adaptive streaming over HTTP (DASH) - Part 1: Media presentation description and segment formats |
| Publisher | ISO/IEC |
| URL | https://www.iso.org/standard/83314.html |
| Role | Bibliographic and terminological reference only |
| Provisional BibTeX key | `iso23009_1_2022` |

## Use Policy

- Do not include the standard PDF in the repository.
- Do not quote long passages from the standard.
- Use the standard to normalize terminology in the TFG.
- When wording is needed in the thesis, paraphrase and cite the standard.
- Keep implementation behavior based on the local client contract, not on copied standard text.

## Terminology To Align

| term | use in TFG |
| --- | --- |
| MPD | Manifest document that describes periods, adaptation sets, representations, and segment addressing. |
| Period | Time-bounded part of a media presentation. |
| Adaptation Set | Grouping of interchangeable encoded components such as video or audio alternatives. |
| Representation | One encoded alternative with bitrate and format metadata. |
| Segment | Addressable media unit requested by the client. |
| HTTP GET / partial GET | Transport mechanism for retrieving MPD and media resources. |
| DASH client | Client-side logic that fetches the MPD, selects representations, requests segments, buffers media, and adapts selections. |

## Boundary For This Repo

The standard reference does not create new runtime requirements in this block. It only informs documentation and later terminology consistency.
