# Experiment Design (Draft)

> **Status:** All arms are **planned** or **scaffolded** unless noted. No results are reported in this repository yet.

## Comparison arms

| # | Arm | Purpose | Input | Training | Role in comparison | Implementation status |
|---|-----|---------|-------|----------|-------------------|-------------------------|
| 1 | **Base RAG** | Retrieval + generation without conflict-specific training | Question + retrieved passages | No | Lower bound; measures default parametric bias vs. context | **scaffolded** (`rag/pipeline_stub.py`, `configs/rag_base.yaml`) |
| 2 | **Conflict-aware prompting** | Test whether instructions alone improve resolution | Question + passages + conflict-aware prompt | No | Non-trained upper bound for prompting; vs. internalized learning | **planned** (`prompts/conflict_aware_prompt.md`, `configs/prompting_conflict_aware.yaml`) |
| 3 | **PA-RAG-style LoRA** | Replicate PA-RAG alignment axes (informativeness, robustness, citation) without conflict-specific data | PA-RAG-style preference data (TBD) | Yes (DPO + LoRA) | Isolate benefit of standard PA-RAG criteria without conflict criterion | **planned** (`configs/lora_parrag_style.yaml`, `finetuning/`) |
| 4 | **Conflict-Aware RAG LoRA** | Train only on conflict preference pairs | Conflict annotations / DPO pairs | Yes (DPO + LoRA) | Measure conflict-only internalization | **planned** (`configs/lora_conflict_only.yaml`) |
| 5 | **Conflict-Aware PA-RAG LoRA** | Combine PA-RAG-style stages with conflict preferences | Multi-stage data + conflict pairs (TBD) | Yes (DPO + LoRA) | **Main proposed** integrated method | **planned** (`configs/lora_conflict_parrag.yaml`) |

## Per-arm detail

### 1. Base RAG

- **Purpose:** Establish baseline behavior when retrieval provides conflicting external evidence.
- **Input:** User question; top-k retrieved chunks; base RAG prompt (`prompts/base_rag_prompt.md`).
- **Training:** None.
- **Expected role:** Reference for faithfulness and conflict-resolution errors.

### 2. Conflict-aware prompting

- **Purpose:** Determine how much conflict handling improves without weight updates.
- **Input:** Same retrieval as Base RAG; `prompts/conflict_aware_prompt.md`.
- **Training:** None.
- **Expected role:** Compare against LoRA arms to separate **instruction** vs. **internalization**.

### 3. PA-RAG-style LoRA

- **Purpose:** Align generator to PA-RAG criteria excluding explicit conflict curriculum.
- **Input:** Standard RAG prompts + PA-RAG preference structure (dataset TBD).
- **Training:** DPO + LoRA (hyperparameters in config — TBD).
- **Expected role:** Control for “better RAG alignment” without conflict labels.

### 4. Conflict-Aware RAG LoRA

- **Purpose:** Train solely on conflict resolution preferences (`data/schema/preference_pair.schema.json`).
- **Input:** Conflict-annotated or pair-derived prompts.
- **Training:** DPO + LoRA on chosen/rejected pairs.
- **Expected role:** Direct test of conflict internalization without full PA-RAG staging.

### 5. Conflict-Aware PA-RAG LoRA

- **Purpose:** Integrate PA-RAG multi-criterion alignment with conflict preference data.
- **Input:** Staged or combined preference data (protocol TBD).
- **Training:** DPO + LoRA.
- **Expected role:** Primary proposed method; compare to arms 1–4.

## Evaluation (TBD)

- Quantitative metrics and judge protocol not finalized — see `benchmark_selection.md` and `eval/README.md`.
- Qualitative error analysis template: `results/README.md` per-run `error_analysis.md`.

## Reference (not a runnable arm in-repo)

- **Full fine-tuning PA-RAG (original paper):** Cited for comparison only; not reproduced here due to compute constraints.
