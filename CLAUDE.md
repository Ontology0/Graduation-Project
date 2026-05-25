# CLAUDE.md

## Project layout conventions

- Center the layout on `src/rag/`, `src/training/`, `src/evaluation/`, `data/`, and `outputs/`.
- Put retrieval pipelines and retrieval experiments in `src/rag/`.
- Put model adaptation scripts and configs in `src/training/`.
- Put benchmark and judge/evaluation scripts in `src/evaluation/` once the protocol exists.
- Put datasets and preprocess outputs in `data/`.
- Put generated metrics, reports, and artifacts in `outputs/`.
- Put experiment YAML configs in `configs/experiments/` and prompt templates in `configs/prompts/`.

## AI assistant behavior

- Do **not** invent experiment outcomes, numeric scores, RAGAS values, accuracy, or benchmark rankings. If something is not implemented or not measured, say so.
- When describing the repo, separate **implemented** (e.g. RAG pipeline modules), **planned** (documented intent), and **not decided** (benchmark, dataset, eval protocol).
- Prefer extending real code from `src/rag/pipeline.py`, `src/training/train.py`, and `src/evaluation/evaluate.py` rather than adding parallel mystery scripts.
- Never commit API keys, secrets, or raw datasets that should stay local or external; use `.env.example` and documented download steps instead.

## README maintenance

- During **snapshot-only** housekeeping, avoid large README rewrites unless they correct factual repo state. Subfolder `README.md` files should stay honest about what exists vs. what is planned.
