# lora_conflict_only — dry-run smoke evidence

Pipeline smoke test for the conflict-only LoRA arm (`configs/experiments/lora_conflict_only.yaml`).  
**Not a training result.** Full QLoRA training on GPU is planned separately.

## Run command

From the repository root (local run used `experiment_name: lora_conflict_only` so outputs land in this folder):

```powershell
$env:HF_HOME = "D:\hf_cache"
python -m src.training.train `
  --config configs/experiments/lora_conflict_only.yaml `
  --dry-run --max-steps 1
```

## Environment

| Item | Value |
|------|--------|
| Model | `microsoft/phi-2` (CPU, no 4-bit in dry-run) |
| Device | CPU |
| HF cache | `HF_HOME=D:\hf_cache` (model weights not on C:) |
| Steps | `--max-steps 1` |
| Data | `data/synthetic_conflicts/preference_pairs_train.jsonl` (2 pairs capped in dry-run) |

## Artifacts in this folder

| File | Meaning |
|------|---------|
| `training_log.jsonl` | One line from `TrainingLogCallback` after step 1 (real dry-run metrics). |
| `trainer_state.json` | Hugging Face `Trainer` state after 1 step (copied from `checkpoint-1/`). |

Weights (`*.safetensors`, `*.bin`, `pytorch_model*`, optimizers, etc.) under this tree are **gitignored** and must not be committed.

## Config vs output path

- Config file: `configs/experiments/lora_conflict_only.yaml`
- For this smoke run, `experiment_name` was set to `lora_conflict_only` locally so checkpoints write here.
- Committed YAML may still use another `experiment_name`; align before a production run.

**스모크용. 학습 결과 아님. 본 학습은 GPU 환경에서 별도 진행.**
