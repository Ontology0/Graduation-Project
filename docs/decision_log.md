# Decision Log (Draft)

> Living document for project decisions. Update when choices are confirmed or reversed.

## Confirmed

- **Conflict focus:** Primary research target is **context–memory conflict** (retrieved external context vs. internal/parametric knowledge).
- **Preference format:** **Chosen/rejected pairs** for DPO-style training (see `data/schema/preference_pair.schema.json`).
- **Compute strategy:** Primary training path is **DPO + LoRA**, not full fine-tuning as in original PA-RAG.
- **Repository role:** This repo is a **research scaffold**; `src/rag/` is a first working draft; `src/training/` and `src/evaluation/` remain entrypoint scaffolds.

## Deferred (pending)

- **Final benchmark(s)** and train/eval split (see `benchmark_selection.md`).
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
| TBD | Benchmark lock | Record here when finalized |
