# Experiment Design (Draft)

> **Status:** All arms are **planned** or **scaffolded** unless noted. No results are reported in this repository yet.

## Comparison arms

| # | Arm | Purpose | Input | Training | Role in comparison | Implementation status |
|---|-----|---------|-------|----------|-------------------|-------------------------|
| 1 | **Base RAG** | Retrieval + generation without conflict-specific training | Question + retrieved passages | No | Lower bound; measures default parametric bias vs. context | **first draft** (`src/rag/pipeline.py`, `configs/experiments/rag_base.yaml`) |
| 2 | **Conflict-aware prompting** | Test whether instructions alone improve resolution | Question + passages + conflict-aware prompt | No | Non-trained upper bound for prompting; vs. internalized learning | **planned** (`configs/prompts/conflict_aware.md`, `configs/experiments/prompting_conflict_aware.yaml`) |
| 3 | **PA-RAG-style LoRA** | Replicate PA-RAG alignment axes (informativeness, robustness, citation) without conflict-specific data | PA-RAG-style preference data (TBD) | Yes (DPO + LoRA) | Isolate benefit of standard PA-RAG criteria without conflict criterion | **planned** (`configs/experiments/lora_parrag_style.yaml`, `src/training/`) |
| 4 | **Conflict-Aware RAG LoRA** | Train only on conflict preference pairs | Conflict annotations / DPO pairs | Yes (DPO + LoRA) | Measure conflict-only internalization | **planned** (`configs/experiments/lora_conflict_only.yaml`) |
| 5 | **Conflict-Aware PA-RAG LoRA** | Combine PA-RAG-style stages with conflict preferences | Multi-stage data + conflict pairs (TBD) | Yes (DPO + LoRA) | **Main proposed** integrated method | **planned** (`configs/experiments/lora_conflict_parrag.yaml`) |

## Per-arm detail

### 1. Base RAG

- **Purpose:** Establish baseline behavior when retrieval provides conflicting external evidence.
- **Input:** User question; top-k retrieved chunks; base RAG prompt (`configs/prompts/base_rag.md`).
- **Training:** None.
- **Expected role:** Reference for faithfulness and conflict-resolution errors.

### 2. Conflict-aware prompting

- **Purpose:** Determine how much conflict handling improves without weight updates.
- **Input:** Same retrieval as Base RAG; `configs/prompts/conflict_aware.md`.
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

## Resolution Rule Justifiability — Conflict Type Scoping

Self-evident resolution rules are required for **DPO train labels**: the preferred response must follow from the conflict setup without subjective adjudication. Types that admit multiple reasonable resolutions are scoped to **eval / capability mapping** only.

| Conflict type | Scoping | 정답 근거 | 라벨 신뢰도 |
|---------------|---------|-----------|-------------|
| **version_update** | Train (self-evident) | Document carries explicit recency or authority markers (version id, “latest”, effective date); gold follows the authoritative source | High — rule is inspectable from metadata/text |
| **temporal** | Train (self-evident) | Time fields or event ordering in context vs. question date make the correct fact determinate | High — temporal logic fixes the label |
| **true_doc vs. false_doc co-present** (exp2 type B; `has_true_doc: true`) | Train (self-evident) | One retrieved passage is marked true relative to fixed `gold`; chosen = follow true doc / reject false doc | High — binary doc quality is given in the benchmark or pilot schema |
| **false_doc only + model_knows** (exp2 type A; `has_true_doc: false`) | Eval only (controversial) | No true passage in retrieval; label depends on whether to trust parametric knowledge vs. misleading context — priority is annotator- or rubric-dependent | Low — “context vs. parametric” trade-off is not self-evident |
| **Debate / multi-answer** (WikiContradict; CONFLICTS opinion / complementary) | Eval only (controversial) | No single gold resolution; multiple defensible answers or stance aggregation | Low — not suitable for chosen/rejected DPO supervision |

## Evaluation (TBD)

- Quantitative metrics and judge protocol not finalized — see `benchmark_selection.md` and `src/evaluation/README.md`.
- Qualitative error analysis template: per-run `error_analysis.md` under `outputs/` (see `outputs/.gitkeep`).

## Reference (not a runnable arm in-repo)

- **Full fine-tuning PA-RAG (original paper):** Cited for comparison only; not reproduced here due to compute constraints.
