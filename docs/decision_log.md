# Decision Log (Draft)

> Living document for project decisions. Update when choices are confirmed or reversed.

## Confirmed

- **Conflict focus:** Primary research target is **context–memory conflict** (retrieved external context vs. internal/parametric knowledge).
- **Preference format:** **Chosen/rejected pairs** for DPO-style training (see `data/schema/preference_pair.schema.json`).
- **Compute strategy:** Primary training path is **DPO + LoRA**, not full fine-tuning as in original PA-RAG.
- **Repository role:** This repo is a **research scaffold**; stubs in `rag/`, `finetuning/`, `eval/` define entrypoints only.

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
- **Reporting fabricated metrics** or implying completed experiments in docs or `results/`.

## History

| Date | Decision | Notes |
|------|----------|-------|
| 2026-05 (scaffold) | `doc/` → `docs/` + `submission_materials/` | Preserve course/submission files under English paths |
| TBD | Benchmark lock | Record here when finalized |
