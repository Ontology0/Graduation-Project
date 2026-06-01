# CLAUDE.md

AI assistant guide for the **Alltology / Conflict-Aware PA-RAG** graduation research repo (이화여대 졸업프로젝트 2026).

## Project snapshot

- **Topic:** Context–memory knowledge conflict in RAG; extend PA-RAG-style preference learning with DPO + LoRA.
- **Scope:** Context–memory conflict is **in scope**; inter-context and intra-memory conflict are **not** the main research target.
- **Repo role:** Research **scaffold** — RAG is a first working draft; training and evaluation are scaffolds; **no final benchmark scores are reported yet.**

| Area | Status |
|------|--------|
| `src/rag/` | **Implemented (first draft)** — load → chunk → embed → retrieve → generate → report |
| `src/chatbot/` | **Implemented** — Telegram repo-KB RAG bot |
| `src/training/` | **Scaffold** — DPO + LoRA entrypoint only |
| `src/evaluation/` | **Scaffold** — placeholder metrics, no fabricated scores |
| Benchmark / eval protocol | **TBD** — see `docs/benchmark_selection.md`, `docs/decision_log.md` |
| LoRA experiment arms | **Config scaffold** — `configs/experiments/lora_*.yaml` |

## Project layout conventions

Center work on `src/rag/`, `src/training/`, `src/evaluation/`, `src/chatbot/`, `data/`, `configs/`, and `outputs/`.

```
Graduation-Project/
├── src/
│   ├── rag/              # RAG pipeline (core research code)
│   ├── chatbot/          # Telegram bot logic
│   ├── training/         # DPO + LoRA (scaffold)
│   └── evaluation/       # Eval harness (scaffold)
├── scripts/              # CLI entrypoints (prefer these over ad-hoc duplicates)
├── configs/
│   ├── experiments/      # YAML experiment arms (rag_base, prompting, lora_*, rag_github_bot)
│   └── prompts/          # Markdown prompt templates (base_rag, conflict_aware, judge, github_bot)
├── data/
│   ├── schema/           # JSON Schema (conflict annotation, preference pairs)
│   ├── sample_docs/      # Local smoke / demo documents
│   ├── synthetic_conflicts/  # Pilot JSONL for batch runs
│   ├── synthetic/        # Planned DPO data (mostly empty)
│   └── natural/          # Planned case study (mostly empty)
├── outputs/              # Generated artifacts only (.gitkeep tracked; runs/index/checkpoints)
├── docs/                 # Research design, ops, verification, presentation
├── course/               # Course submissions (elevator speech, team docs) — not runtime code
├── tests/                # pytest suite
├── experiments/          # Ad-hoc pilot scripts (e.g. pilot_2025-05-26/) — not the main pipeline
├── app.py                # HuggingFace Spaces Gradio demo entrypoint
└── CONTRIBUTING.md       # Branch strategy, commit format, PR flow
```

**Placement rules**

- Retrieval pipelines and RAG experiments → `src/rag/`; run via `scripts/run_pipeline.py` or `scripts/run_batch.py`.
- Telegram bot logic → `src/chatbot/`; run via `scripts/telegram_bot.py`.
- Model adaptation → `src/training/` + `configs/experiments/lora_*.yaml`.
- Benchmark / judge / scoring → `src/evaluation/` once protocol exists (`configs/prompts/judge.md` is rubric draft only).
- Datasets and preprocess outputs → `data/`; do not commit secrets or large private dumps.
- Metrics, run reports, indexes, checkpoints → `outputs/` (e.g. `outputs/runs/`, `outputs/index/`).
- Research and ops docs → `docs/`; course-only material → `course/`.
- Experiment YAML → `configs/experiments/`; prompt templates → `configs/prompts/`.

## Key entrypoints

| Task | Entry |
|------|--------|
| Single-question RAG smoke | `make demo` or `scripts/run_pipeline.py` + `configs/experiments/rag_base.yaml` |
| Base vs conflict-aware compare | `make demo-conflict` |
| Batch over pilot JSONL | `scripts/run_batch.py` + `data/synthetic_conflicts/pilot_conflicts.jsonl` |
| Telegram bot (local) | `scripts/telegram_bot.py` + `configs/experiments/rag_github_bot.yaml` |
| HF Spaces demo | `app.py` |
| Training (scaffold) | `python -m src.training.train` |
| Evaluation (scaffold) | `python -m src.evaluation.evaluate` |
| Unit tests | `pytest -q` (see `pyproject.toml`) |

Secrets: copy `.env.example` → `.env` (gitignored). Never commit API keys or tokens.

## Docs map (read before guessing)

| Need | File |
|------|------|
| Repo status / demo links | `README.md` |
| Smoke test & demo evidence | `docs/demo.md` |
| Architecture 1-pager | `docs/architecture.md` |
| RQ ↔ code alignment | `docs/rq_to_implementation_map.md` |
| Confirmed vs deferred decisions | `docs/decision_log.md` |
| Repro / ops verification | `docs/verification_checklist.md` |
| Telegram ops & security | `docs/telegram_bot_ops.md` |
| RAG module detail | `src/rag/README.md` |
| Git / PR conventions | `CONTRIBUTING.md` |
| AI tool usage transparency | `docs/ai_transparency_report.md` |

**Suggested read order for new contributors:** README 저장소 상태 → `docs/decision_log.md` → `docs/experiment_design.md` → `src/rag/pipeline.py`.

## Git workflow

- Daily work: branch from **`dev`** → PR to **`dev`** → team review → merge.
- **`main`**: submission / release snapshots only; merge via `dev → main` PR when milestone agreed.
- Commit format: `태그: 내용(#이슈번호)` — tags: `feat`, `fix`, `docs`, `refactor`, `chore` (see `CONTRIBUTING.md`).
- Do not push directly to `main`; do not PR feature branches straight to `main`.

## AI assistant behavior

- Do **not** invent experiment outcomes, numeric scores, RAGAS values, accuracy, or benchmark rankings. If something is not implemented or not measured, say so.
- When describing the repo, separate **implemented**, **planned** (documented intent), and **not decided** (benchmark, dataset, eval protocol).
- Prefer extending real code from `src/rag/pipeline.py`, `src/training/train.py`, and `src/evaluation/evaluate.py` rather than adding parallel mystery scripts.
- Prefer `scripts/run_pipeline.py`, `scripts/run_batch.py`, and `scripts/telegram_bot.py` over new one-off runners unless there is a clear gap.
- Never commit API keys, secrets, `.env`, or raw datasets that should stay local; use `.env.example` and documented download steps.
- Keep docs honest: scaffold ≠ completed experiment. Align README/subfolder READMEs with `docs/decision_log.md`.
- Telegram bot: sensitive commands (`/reindex`, `/save`, `/status`) require allowlist; see `docs/telegram_bot_ops.md`.

## README maintenance

- During **snapshot-only** housekeeping, avoid large README rewrites unless they correct factual repo state.
- Subfolder `README.md` files (`src/rag/`, `src/evaluation/`, etc.) should stay honest about what exists vs. what is planned.
- README holds summaries; detailed ops (Telegram, verification) live in `docs/`.
