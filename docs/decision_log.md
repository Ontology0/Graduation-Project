# Decision Log (Draft)

> Living document for project decisions. Update when choices are confirmed or reversed.

## Confirmed

- **Conflict focus:** Primary research target is **context–memory conflict** (retrieved external context vs. internal/parametric knowledge).
- **Preference format:** **Chosen/rejected pairs** for DPO-style training (see `data/schema/preference_pair.schema.json`).
- **Compute strategy:** Primary training path is **DPO + LoRA**, not full fine-tuning as in original PA-RAG.
- **Repository role:** This repo is a **research scaffold**; `src/rag/` is a first working draft; `src/training/` and `src/evaluation/` remain entrypoint scaffolds.
- **Benchmark train/eval split (issue #55):** Documented in `docs/benchmark_selection.md`. **Train** = unambiguous DPO labels only (version/time authority, **true_doc vs. false_doc**, clear context–memory resolution). **Eval** = held-out quantitative partitions plus **controversial** slices (**false_doc-only**, **model_knows** / low-confidence parametric cases) and natural/debate sets (WikiContradict; CONFLICTS opinion/complementary types). **Reference-only:** CONFLICTS taxonomy for schema/judge; not bulk training. **Not train:** WikiContradict; ambiguous multi-answer conflicts. Preprocessing scripts and exact subset sizes are **not implemented** yet.

## Deferred (pending)
- **Final evaluation metrics** (RAGAS subsets, conflict-resolution accuracy, LLM-judge rubric weights).
- **Retrieval backend:** OpenSearch vs. local FAISS/Chroma for experiments at scale.
- **Circuit-domain dataset** as a dedicated case study (yes/no and scope).
- **Base generator model** and embedding model IDs.
- **PA-RAG stage replication** detail (which stages run before conflict DPO).

## Excluded (for this project’s main line)

- **Inter-context conflict** as the **primary** research object (may appear in data but not as the core problem statement).
- **Intra-memory conflict** as a dedicated analysis track (parametric self-contradiction without retrieval conflict).
- **Reporting fabricated metrics** or implying completed experiments in docs or `outputs/`.

## History

| Date | Decision | Notes |
|------|----------|-------|
| 2026-05 (scaffold) | Course materials under `course/` | Former `doc/` / submission paths consolidated |
| 2026-05 (paths) | `results/` → `outputs/`, prompts under `configs/prompts/` | Align docs and configs with `src/` layout |
| 2026-05 (ops) | Telegram bot ops doc in `docs/telegram_bot_ops.md` | Keep README research-focused; document cost/security knobs separately |
| 2026-06-01 | Benchmark train/eval split (#55) | Train/eval roles and principles in `benchmark_selection.md`; metrics/protocol still TBD |
