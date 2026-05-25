# data/

## Purpose

Holds datasets and preprocessing outputs for retrieval, fine-tuning, and evaluation once a benchmark and data policy are chosen.

## Current status

No concrete dataset is committed or finalized yet. Paths and formats will be added when the benchmark and protocol are decided.

## Layout

| Subfolder | Purpose |
|---|---|
| `schema/` | JSON Schema for conflict annotations and DPO preference pairs (`example_annotation.json` is fictitious) |
| `synthetic/` | DPO training data — synthetic conflict with unambiguous ground truth |
| `natural/` | Natural conflict case studies for limitation / qualitative analysis only |

See each subfolder's `README.md` for status and git policy.

## Git policy

Do not commit sensitive data, credentials, or large binaries. Prefer `.gitignore`, documented download steps, or external storage for heavy assets.
