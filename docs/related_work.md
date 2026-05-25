# Related Work (Draft)

> **Status:** Detailed summaries are **not complete**. Each entry is a **citation placeholder** for literature review expansion.

## Knowledge Conflicts for LLMs: A Survey

- **Placeholder:** Xu et al. (survey on knowledge conflict types and mitigation) — EMNLP 2024 or equivalent survey citation TBD.
- **Relevance:** Taxonomy of conflict types; motivates narrowing to **context–memory** for this project.
- **Summary:** *To be written.*

## Adaptive Chameleon or Stubborn Sloth

- **Placeholder:** Xie et al., ICLR 2024 — *Adaptive Chameleon or Stubborn Sloth: Reconciling Conflicting Knowledge in LLMs*.
- **Relevance:** How LLMs behave when parametric and contextual knowledge disagree.
- **Summary:** *To be written.*

## Entity-Based Knowledge Conflicts in Question Answering

- **Placeholder:** Longpre et al., EMNLP 2021 — entity substitution / synthetic conflict construction.
- **Relevance:** Methodology for building controlled conflict QA pairs.
- **Summary:** *To be written.*

## PA-RAG

- **Placeholder:** PA-RAG (preference-aligned RAG generator) — base paper for informativeness, robustness, citation alignment.
- **Relevance:** Multi-stage preference optimization; **does not explicitly target knowledge conflict** in the original framing.
- **Local notes:** `docs/submission_materials/PA-RAG_paper/PA-RAG_reading.md`
- **Summary:** *To be written.*

## Context-DPO / context-faithfulness

- **Placeholder:** Context-DPO and related **context-faithfulness** / preference learning work (exact papers TBD).
- **Relevance:** Aligning generators to follow retrieved context; complementary to conflict-specific chosen/rejected pairs.
- **Summary:** *To be written.*

## Additional references (from project README, TBD in prose)

| Topic | Placeholder | Notes |
|-------|-------------|-------|
| RAG conflict resolution | Jin et al., LREC-COLING 2024 (Tug-of-war) | Direct methodological neighbor |
| Benchmarks | ClashEval, ConflictBank, WikiContradict | See `benchmark_selection.md` |
