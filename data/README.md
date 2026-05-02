# data/

## Purpose

Holds datasets and preprocessing outputs for retrieval, fine-tuning, and evaluation once a benchmark and data policy are chosen.

## Current status

No concrete dataset is committed or finalized yet. Paths and formats will be added when the benchmark and protocol are decided.

## Planned layout

Subfolders such as `raw/` and `processed/` may be introduced later to separate source dumps from cleaned or tokenized artifacts.

## Git policy

Do not commit sensitive data, credentials, or large binaries. Prefer `.gitignore`, documented download steps, or external storage for heavy assets.
