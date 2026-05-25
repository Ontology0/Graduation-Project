# Self Demo (Placeholder)

> **Status:** to be updated — no recorded demo yet.

## Demo goal

Show a **context–memory conflict** scenario where retrieved evidence and the model’s default answer disagree, and compare how each method resolves the conflict (or abstains).

## Demo scenario

- **Setting:** Single user question with one retrieved passage that contradicts the answer the base model would give without conflict instructions.
- **Example type:** Fictional or clearly labeled synthetic domain (no real-world entity claims requiring verification).
- **To be updated:** Concrete question, context block, and resolution rule once a pilot dataset slice exists.

## Compared methods

| Method | Config / prompt |
|--------|-----------------|
| Base RAG | `configs/rag_base.yaml`, `prompts/base_rag_prompt.md` |
| Conflict-aware prompting | `configs/prompting_conflict_aware.yaml`, `prompts/conflict_aware_prompt.md` |
| PA-RAG-style LoRA | `configs/lora_parrag_style.yaml` (when trained) |
| Conflict-Aware RAG LoRA | `configs/lora_conflict_only.yaml` (when trained) |
| Conflict-Aware PA-RAG LoRA | `configs/lora_conflict_parrag.yaml` (when trained) |

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
- Link to `docs/experiment_design.md` and `results/` for reproducible run folders when available.
