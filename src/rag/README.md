# src/rag/

## Purpose

RAG baseline pipeline: ingest domain text, build a retriever, and call a generator with retrieved context.

## Architecture

```text
documents ─→ document_loader ─→ chunker ─→ embedder ─→ vector_store
                                                           │
query ─→ retriever (embed + search) ─→ prompt_builder ─→ generator ─→ answer
```

## Modules

| Module | Description |
|--------|-------------|
| `config.py` | Load YAML experiment configs and `.env` secrets |
| `document_loader.py` | Load `.txt`, `.md`, `.json`, `.jsonl` files into `Document` objects |
| `chunker.py` | Split documents into overlapping chunks with sentence-boundary awareness |
| `embedder.py` | Generate dense embeddings via `sentence-transformers` |
| `vector_store.py` | FAISS-backed vector store with save/load support |
| `retriever.py` | Query-to-document search combining embedder and vector store |
| `prompt_builder.py` | Build chat-style prompts with base or conflict-aware templates |
| `generator.py` | HuggingFace causal LM wrapper for text generation |
| `pipeline.py` | End-to-end orchestrator |

## Quick start

```bash
python scripts/run_pipeline.py \
    --config configs/experiments/rag_base.yaml \
    --docs data/sample_docs/ \
    --question "What is knowledge conflict in RAG?"
```

## Current status

`src/rag/` is a **first working draft** (load → chunk → embed → retrieve → generate). It is **not** benchmark-validated yet.

Remaining work:

- Dataset and benchmark selection (see `docs/benchmark_selection.md`)
- Evaluation metrics integration (see `src/evaluation/`)
- LoRA adapter loading for fine-tuned model variants
