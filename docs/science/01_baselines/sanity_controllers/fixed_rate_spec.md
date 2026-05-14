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

- Whether the config stores a target rate or a fixed representation index.
- How invalid fixed values are handled.
- Whether the controller name should be `fixed_rate` or map to the existing debug naming.

## Non-Goals

- Do not use as an academic baseline.
- Do not compare as an ABR algorithm.
- Do not modify runtime metrics.
