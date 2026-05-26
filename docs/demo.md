# Self Demo (Placeholder)

> **Status:** to be updated — no recorded demo yet.

## Demo goal

Show a **context–memory conflict** scenario where retrieved evidence and the model’s default answer disagree, and compare how each method resolves the conflict (or abstains).

## Demo scenario

- **Setting:** Single user question with one retrieved passage that contradicts the answer the base model would give without conflict instructions.
- **Example type:** Fictional or clearly labeled synthetic domain (no real-world entity claims requiring verification).
- **Sample document:** `data/sample_docs/example_conflict.txt` (fictional Northwood Institute mascot color revision).
- **To be updated:** Concrete question, context block, and resolution rule once a pilot dataset slice exists.

## Quick run (smoke test)

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

No demo metrics or recorded outcomes yet — use this only to verify the pipeline wiring.

## Compared methods

| Method | Config / prompt |
|--------|-----------------|
| Base RAG | `configs/experiments/rag_base.yaml`, `configs/prompts/base_rag.md` |
| Conflict-aware prompting | `configs/experiments/prompting_conflict_aware.yaml`, `configs/prompts/conflict_aware.md` |
| PA-RAG-style LoRA | `configs/experiments/lora_parrag_style.yaml` (when trained) |
| Conflict-Aware RAG LoRA | `configs/experiments/lora_conflict_only.yaml` (when trained) |
| Conflict-Aware PA-RAG LoRA | `configs/experiments/lora_conflict_parrag.yaml` (when trained) |

## Demo result table (template)

| Method | Follows evidence? | States conflict? | Resolution correct? | Notes |
|--------|-------------------|------------------|---------------------|-------|
| Base RAG | TBD | TBD | TBD | |
| Conflict-aware prompting | TBD | TBD | TBD | |
| PA-RAG-style LoRA | TBD | TBD | TBD | |
| Conflict-Aware RAG LoRA | TBD | TBD | TBD | |
| Conflict-Aware PA-RAG LoRA | TBD | TBD | TBD | |

*No numeric scores — fill after live demo runs.*

## Demo video

- **URL:** `TODO` (e.g., presentation recording link)

## Notes for final presentation

- Emphasize **context–memory** scope; inter-context and intra-memory are out of main scope.
- State clearly that results are **pilot / preliminary** until benchmark eval is complete.
- Link to `docs/experiment_design.md` and `outputs/` for reproducible run folders when available.
