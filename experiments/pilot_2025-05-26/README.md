# Local pilot validation (2025-05-26)

## Purpose

Record the **local sanity-check** stage before the main experiment run.  
This pilot validates wiring (config → pipeline → prompts → dataset → batch script).  
**Not** the final benchmark: full experiments are planned on **Colab with Llama 3.1-8B**.

No benchmark scores or paper-ready conclusions are implied by artifacts in this folder.

## Environment (this run)

| Item | Value |
|------|--------|
| OS | Windows 11 |
| Hardware | CPU only |
| Python | 3.13 |
| Generator (sanity) | `microsoft/phi-2` via Hugging Face |
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` |

Phi-2 was used only to confirm that retrieval + generation execute end-to-end on a developer machine.

## Scripts

| Script | Role |
|--------|------|
| `01_check_config.py` | Verify YAML configs map to pipeline fields (`experiment_name`, generator model, `top_k`, chunking, `generation`, `prompt_file`). |
| `02_diff_prompts.py` | Confirm `base_rag.md` and `conflict_aware.md` parse to **different** system/user templates. |
| `03_e2e_real.py` | One real forward pass: index `data/sample_docs/`, single question, write full `RAGResult` to `results/e2e_result.txt`. |
| `04_check_dataset.py` | Validate `data/synthetic_conflicts/pilot_conflicts.jsonl` (10 cases, stances, required keys). |

Each script prepends the repository root to `sys.path` so imports work when run from any cwd.

## `results/` artifacts

| File | Source |
|------|--------|
| `e2e_result.txt` | Output of `03_e2e_real.py` (full `RAGResult` repr; phi-2 may ramble — qualitative wiring check only). |
| `base_rag_2cases.jsonl` | `scripts/run_batch.py --config configs/experiments/rag_base.yaml --limit 2` (copied from `outputs/base_rag/pilot_conflicts_20260526_113608.jsonl`). |
| `conflict_aware_prompting_2cases.jsonl` | Same with `prompting_conflict_aware.yaml` (from `outputs/conflict_aware_prompting/pilot_conflicts_20260526_114950.jsonl`). |

Each JSONL line: `case_id`, `question`, `gold_answer`, `predicted_answer`, `retrieved_sources`, `config_name`, `conflict_type`, optional `generation` metadata.

## Reproduce

From the repository root:

```powershell
$env:PYTHONPATH = "."

python experiments/pilot_2025-05-26/01_check_config.py
python experiments/pilot_2025-05-26/02_diff_prompts.py
python experiments/pilot_2025-05-26/04_check_dataset.py

# Slow: loads phi-2 on CPU
python experiments/pilot_2025-05-26/03_e2e_real.py

# Batch smoke (2 cases per arm)
python scripts/run_batch.py --config configs/experiments/rag_base.yaml --dataset data/synthetic_conflicts/pilot_conflicts.jsonl --limit 2
python scripts/run_batch.py --config configs/experiments/prompting_conflict_aware.yaml --dataset data/synthetic_conflicts/pilot_conflicts.jsonl --limit 2
```

Fresh batch outputs go under `outputs/{experiment_name}/`; copy the latest JSONL here if you re-run the pilot.
