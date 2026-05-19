# Fixed-Rate Sanity Controller Spec

## Purpose

`fixed_rate` is a sanity controller, not an academic ABR baseline. It is used to validate controller plumbing, quantization, telemetry, and fake-engine reproducibility.

## Behavior

| item | value |
| --- | --- |
| input | representation ladder and configured fixed target rate or fixed level |
| output | target rate in bytes per second |
| selection | always request the configured target, then rely on quantization |
| state | no adaptive state |
| QoE claim | none |

## Required Decisions Before Code

- Status: implemented as canonical controller name `fixed_rate`.
- Module: `core/controller/sanity_rate.py`.
- Config supports fixed representation index through `level`, `quality_level`, or `fixed_level`.
- Config supports fixed target rate through `target_rate`, `fixed_rate`, or `rate`.
- Target-rate units default to bytes per second; explicit `target_rate_unit` / `rate_unit` can be `bytes_per_second`, `bps`, `kbps`, or `mbps`.
- Invalid or missing fixed values fall back safely to the minimum representation.
- Out-of-range levels and rates clamp to the nearest valid ladder floor/edge.

## Implemented Edge Behavior

| case | behavior |
| --- | --- |
| no configured level/rate | select minimum representation |
| fixed index below zero | clamp to level 0 |
| fixed index above max | clamp to highest available level |
| fixed target rate below min | select minimum representation |
| fixed target rate above max | select maximum available representation |
| single representation | select level 0 |
| missing, empty or malformed ladder | return safe target `0.0` without crashing |

## Non-Goals

- Do not use as an academic baseline.
- Do not compare as an ABR algorithm.
- Do not modify runtime metrics.
- Do not claim fake smoke output as benchmark evidence.
