# src/rag/

## Purpose

RAG baseline pipeline for this project: ingest text, build a retriever, inject retrieved context into a prompt, and generate an answer.

Supports **local HuggingFace models** (default smoke path) and **API backends** (OpenAI embeddings + Anthropic generation for the Telegram bot config). Conflict-aware prompt templates live in `configs/prompts/` and are loaded via YAML `prompt_file`.

## Architecture

```text
documents ─→ document_loader ─→ chunker ─→ embedder ─→ vector_store ──┐
                     │                              ↑ save/load index │
                     │                              │ (retrieval.index_dir)
query ─→ retriever (embed + search) ─→ prompt_builder ─→ generator ─→ RAGResult
                                                                          │
                                                                          └─→ reporting → outputs/runs/
```

**Orchestration:** `RAGPipeline` in `pipeline.py` wires the steps above. `RAGResult` carries the answer, retrieved sources, and optional generation metadata.

## Modules

| Module | Description |
|--------|-------------|
| `config.py` | Load YAML experiment configs, resolve repo-relative paths, read `.env` secrets |
| `document_loader.py` | Load `.txt`, `.md`, `.json`, `.jsonl` into `Document` objects |
| `chunker.py` | Split documents into overlapping chunks with sentence-boundary awareness |
| `embedder.py` | Dense embeddings via **SentenceTransformers** (local) or **OpenAI API** (`openai/...` prefix) |
| `vector_store.py` | **FAISS** vector store (default) with **NumPy fallback**; save/load to disk |
| `retriever.py` | Embed query + top-k search over the vector store |
| `prompt_builder.py` | Build chat-style prompts from `configs/prompts/*.md` or built-in base / conflict-aware templates |
| `generator.py` | **HuggingFace causal LM** (`Generator`) or **Anthropic Messages API** (`AnthropicGenerator`) |
| `pipeline.py` | End-to-end orchestrator: index, query, optional index persistence |
| `reporting.py` | Write run artifacts to `outputs/runs/` (JSON + Markdown) |
| `github_kb.py` | Load repo-facing files (`README.md`, `docs/`, etc.) for the Telegram RAG bot |
| `pilot_dataset.py` | Load synthetic conflict pilot cases (JSONL) for batch runs |

## Configuration

Experiments are defined under `configs/experiments/*.yaml`. Common keys:

| Section | Role |
|---------|------|
| `experiment_name` | Label stored in `RAGResult.config_name` |
| `llm.provider` / `llm.model` | `hf` (default) or `anthropic` / `claude` |
| `retrieval.embedding_model` | e.g. `sentence-transformers/all-MiniLM-L6-v2` or `openai/text-embedding-3-small` |
| `retrieval.backend` | `faiss` or `numpy` |
| `retrieval.index_dir` | Optional on-disk index path (reused across restarts) |
| `prompt_file` | Markdown prompt template under `configs/prompts/` |
| `generation` | `max_new_tokens`, `temperature`, etc. |

Example configs:

- **Base RAG (local HF):** `configs/experiments/rag_base.yaml`
- **Conflict-aware prompting:** `configs/experiments/prompting_conflict_aware.yaml`
- **Telegram bot (API):** `configs/experiments/rag_github_bot.yaml`

## Entry points

| Script | Uses `src/rag/` via |
|--------|---------------------|
| `scripts/run_pipeline.py` | Single-question CLI smoke test |
| `scripts/run_batch.py` | JSONL pilot dataset batch runs → `outputs/` |
| `scripts/telegram_bot.py` | `github_kb.load_repo_documents` + `RAGPipeline` |

More context: `docs/architecture.md`, `docs/demo.md`.

## Quick start

**Single question (local HF path; needs model download on first run):**

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

**Batch over pilot cases (when a JSONL dataset is available):**

```bash
python scripts/run_batch.py \
  --config configs/experiments/rag_base.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl \
  --limit 5
```

Success criteria and expected output paths: `docs/demo.md`.

## Current status

`src/rag/` is a **first working draft** (load → chunk → embed → retrieve → generate → report). It is **not benchmark-validated yet**; no final eval scores are reported.

**Implemented**

- YAML-driven pipeline with index save/load
- Base and conflict-aware prompt loading
- Local HF and API (OpenAI embed / Anthropic generate) backends
- Run reporting to `outputs/runs/`
- Repo KB loader and pilot JSONL batch helper

**Remaining work**

- Benchmark and dataset selection (`docs/benchmark_selection.md`)
- Evaluation metrics and protocol (`src/evaluation/`, `docs/experiment_design.md`)
- LoRA adapter loading for fine-tuned model variants (`configs/experiments/lora_*.yaml` are scaffolded)
