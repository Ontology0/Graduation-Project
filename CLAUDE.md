# CLAUDE.md

## Snapshot release conventions

- Center the layout on `rag/`, `finetuning/`, `eval/`, `data/`, and `results/`.
- Put retrieval pipelines and retrieval experiments in `rag/`.
- Put model adaptation scripts and configs in `finetuning/`.
- Put benchmark and judge/evaluation scripts in `eval/` once the protocol exists.
- Put datasets and preprocess outputs in `data/`.
- Put generated metrics, reports, and artifacts in `results/`.

## AI assistant behavior

- Do **not** invent experiment outcomes, numeric scores, RAGAS values, accuracy, or benchmark rankings. If something is not implemented or not measured, say so.
- When describing the repo, separate **implemented** (e.g. stub entrypoints), **planned** (documented intent), and **not decided** (benchmark, dataset, eval protocol).
- Prefer extending real code from `rag/pipeline_stub.py`, `finetuning/train_stub.py`, and `eval/evaluate_stub.py` rather than adding parallel mystery scripts.
- Never commit API keys, secrets, or raw datasets that should stay local or external; use `.env.example` and documented download steps instead.

## README maintenance

- During **snapshot-only** housekeeping, avoid large README rewrites unless they correct factual repo state. Subfolder `README.md` files should stay honest about what exists vs. what is planned.
