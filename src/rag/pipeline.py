"""End-to-end RAG pipeline: load → chunk → embed → retrieve → generate."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.rag.chunker import chunk_documents
from src.rag.config import load_config, load_env
from src.rag.document_loader import Document, load_documents
from src.rag.embedder import Embedder
from src.rag.generator import AnthropicGenerator, GenerationConfig, GenerationOutput, Generator
from src.rag.prompt_builder import (
    PromptTemplate,
    build_prompt,
    default_template,
    load_prompt_template,
)
from src.rag.retriever import Retriever
from src.rag.vector_store import load_vector_store, make_vector_store, save_vector_store

logger = logging.getLogger(__name__)

_DEFAULT_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"
_DEFAULT_MODEL = "microsoft/phi-2"
_DEFAULT_TOP_K = 5
_DEFAULT_CHUNK_SIZE = 512
_DEFAULT_CHUNK_OVERLAP = 128


@dataclass
class RAGResult:
    """Full result of a RAG query including answer and provenance."""

    question: str
    answer: str
    retrieved_sources: list[dict[str, Any]] = field(default_factory=list)
    generation_output: GenerationOutput | None = None
    config_name: str = ""

    def to_dict(self, *, include_generation: bool = True) -> dict[str, Any]:
        """Serialize for JSON/JSONL logging (batch runs, outputs/)."""
        data: dict[str, Any] = {
            "question": self.question,
            "predicted_answer": self.answer,
            "config_name": self.config_name,
            "retrieved_sources": self.retrieved_sources,
        }
        if include_generation and self.generation_output is not None:
            gen = self.generation_output
            data["generation"] = {
                "model_name": gen.model_name,
                "prompt_tokens": gen.prompt_tokens,
                "generated_tokens": gen.generated_tokens,
            }
        return data


class RAGPipeline:
    """Orchestrates retrieval-augmented generation from config to answer."""

    def __init__(
        self,
        retriever: Retriever,
        generator: Generator,
        *,
        experiment_name: str = "",
        prompt_template: PromptTemplate | None = None,
        top_k: int = _DEFAULT_TOP_K,
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = _DEFAULT_CHUNK_OVERLAP,
        generation_config: GenerationConfig | None = None,
    ):
        self.retriever = retriever
        self.generator = generator
        self.experiment_name = experiment_name
        self.prompt_template = prompt_template
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.generation_config = generation_config or GenerationConfig()

    @classmethod
    def from_config(cls, config_path: str | Path) -> RAGPipeline:
        """Build the full pipeline from a YAML config file."""
        load_env()
        cfg = load_config(config_path)

        experiment_name = str(cfg.get("experiment_name") or "")
        llm_cfg = cfg.get("llm", {}) or {}
        provider = (llm_cfg.get("provider") or "hf").lower()
        model_name = llm_cfg.get("model") or cfg.get("model_name") or _DEFAULT_MODEL

        retrieval_cfg = cfg.get("retrieval") or {}
        backend = retrieval_cfg.get("backend") or "faiss"
        index_dir = retrieval_cfg.get("index_dir") or None
        embedding_model = retrieval_cfg.get("embedding_model") or _DEFAULT_EMBEDDING
        top_k = int(retrieval_cfg.get("top_k") or _DEFAULT_TOP_K)
        chunk_size = int(retrieval_cfg.get("chunk_size") or _DEFAULT_CHUNK_SIZE)
        chunk_overlap = int(retrieval_cfg.get("chunk_overlap") or _DEFAULT_CHUNK_OVERLAP)

        prompt_file = cfg.get("prompt_file")
        if prompt_file:
            prompt_template = load_prompt_template(prompt_file)
            logger.info("Loaded prompt template from %s", prompt_file)
        else:
            conflict_aware = "conflict" in experiment_name.lower()
            prompt_template = default_template(conflict_aware)
            logger.info(
                "No prompt_file in config; using built-in template (conflict_aware=%s)",
                conflict_aware,
            )

        generation_config = GenerationConfig.from_dict(cfg.get("generation"))

        embedder = Embedder(model_name=embedding_model)
        store = make_vector_store(backend=str(backend), dimension=embedder.dimension)
        retriever = Retriever(embedder=embedder, store=store, top_k=top_k)
        if provider in ("anthropic", "claude"):
            generator = AnthropicGenerator(model_name=str(model_name))
        else:
            generator = Generator(model_name=str(model_name))

        logger.info(
            "Pipeline config: experiment=%s model=%s top_k=%s chunk=%s/%s",
            experiment_name,
            model_name,
            top_k,
            chunk_size,
            chunk_overlap,
        )

        pipeline = cls(
            retriever=retriever,
            generator=generator,
            experiment_name=experiment_name,
            prompt_template=prompt_template,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            generation_config=generation_config,
        )
        pipeline._retrieval_backend = str(backend)
        pipeline._index_dir = str(index_dir) if index_dir else None
        if pipeline._index_dir:
            pipeline.try_load_index(pipeline._index_dir)
        return pipeline

    def index_documents(
        self,
        source: str | Path | list[Document],
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> int:
        """Load (if path) and index documents into the vector store."""
        size = chunk_size if chunk_size is not None else self.chunk_size
        overlap = chunk_overlap if chunk_overlap is not None else self.chunk_overlap

        if isinstance(source, (str, Path)):
            documents = load_documents(source)
        else:
            documents = source

        chunks = chunk_documents(documents, size, overlap)
        if not chunks:
            logger.warning("No chunks produced from %d documents; nothing indexed.", len(documents))
            return 0
        vectors = self.retriever.embedder.embed([c.text for c in chunks])
        self.retriever.store.add(vectors, chunks)

        logger.info(
            "Indexed %d documents (%d chunks, chunk_size=%d, overlap=%d)",
            len(documents),
            len(chunks),
            size,
            overlap,
        )
        return len(chunks)

    def save_index(self, directory: str | Path) -> None:
        """Save current vector store to disk."""
        save_vector_store(self.retriever.store, directory)

    def load_index(self, directory: str | Path) -> None:
        """Load vector store from disk and replace the current store."""
        backend = str(getattr(self, "_retrieval_backend", "faiss"))
        self.retriever.store = load_vector_store(backend=backend, directory=directory)

    def try_load_index(self, directory: str | Path) -> bool:
        """Attempt to load index. Returns True if loaded, False otherwise."""
        try:
            self.load_index(directory)
            logger.info("Loaded index from %s", directory)
            return True
        except Exception as e:
            logger.info("Index not loaded (%s). Will rebuild when indexing docs.", e)
            return False

    def query(self, question: str, top_k: int | None = None) -> RAGResult:
        """Run the full RAG pipeline for a single question."""
        k = top_k if top_k is not None else self.top_k

        results = self.retriever.retrieve(question, top_k=k)

        messages = build_prompt(
            question=question,
            results=results,
            template=self.prompt_template,
        )

        gen_output = self.generator.generate(messages, config=self.generation_config)

        sources = [
            {"source": r.source, "score": round(r.score, 4), "text": r.text[:200]}
            for r in results
        ]

        return RAGResult(
            question=question,
            answer=gen_output.text,
            retrieved_sources=sources,
            generation_output=gen_output,
            config_name=self.experiment_name,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run RAG pipeline")
    parser.add_argument(
        "--config",
        default="configs/experiments/rag_base.yaml",
        help="Config YAML path",
    )
    parser.add_argument("--docs", required=True, help="Path to documents to index")
    parser.add_argument("--question", required=True, help="Question to ask")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    pipeline = RAGPipeline.from_config(args.config)
    pipeline.index_documents(args.docs)
    result = pipeline.query(args.question)

    print(f"\nExperiment: {result.config_name}")
    print(f"\nQuestion: {result.question}")
    print(f"\nAnswer: {result.answer}")
    print(f"\nSources:")
    for s in result.retrieved_sources:
        print(f"  - [{s['source']}] (score: {s['score']})")
