# finetuning/

## Purpose

Future scripts and configs for parameter-efficient fine-tuning (e.g. LoRA, QLoRA) and optional alignment runs (e.g. DPO), aligned with the chosen model and data.

## Current status

Model family, training dataset, and hyperparameters are **not decided**. This folder intentionally contains **no** checkpoints, metrics, or logs that could be read as real experiment outcomes.

## Layout

| Subfolder | Purpose |
|---|---|
| `dpo/` | DPO training scripts and launch configs |
| `lora/` | LoRA / QLoRA adapter configs and PEFT settings |

`train_stub.py` at this level remains the placeholder entrypoint until real training is wired up.

See each subfolder's `README.md` for current status.
