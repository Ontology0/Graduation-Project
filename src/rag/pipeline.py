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
from src.rag.generator import GenerationConfig, GenerationOutput, Generator
from src.rag.prompt_builder import build_prompt
from src.rag.retriever import Retriever
from src.rag.vector_store import FaissVectorStore

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """Full result of a RAG query including answer and provenance."""

    question: str
    answer: str
    retrieved_sources: list[dict[str, Any]] = field(default_factory=list)
    generation_output: GenerationOutput | None = None
    config_name: str = ""


class RAGPipeline:
    """Orchestrates retrieval-augmented generation from config to answer."""

    def __init__(
        self,
        retriever: Retriever,
        generator: Generator,
        conflict_aware: bool = False,
        top_k: int = 5,
        generation_config: GenerationConfig | None = None,
    ):
        self.retriever = retriever
        self.generator = generator
        self.conflict_aware = conflict_aware
        self.top_k = top_k
        self.generation_config = generation_config or GenerationConfig()

    @classmethod
    def from_config(cls, config_path: str | Path) -> RAGPipeline:
        """Build the full pipeline from a YAML config file."""
        load_env()
        cfg = load_config(config_path)

        retrieval_cfg = cfg.get("retrieval", {})
        embedding_model = retrieval_cfg.get("embedding_model") or "sentence-transformers/all-MiniLM-L6-v2"
        top_k = retrieval_cfg.get("top_k") or 5

        model_name = cfg.get("model_name") or "microsoft/phi-2"
        conflict_aware = "conflict" in cfg.get("experiment_name", "")

        embedder = Embedder(model_name=embedding_model)
        store = FaissVectorStore(dimension=embedder.dimension)
        retriever = Retriever(embedder=embedder, store=store, top_k=top_k)
        generator = Generator(model_name=model_name)

        return cls(
            retriever=retriever,
            generator=generator,
            conflict_aware=conflict_aware,
            top_k=top_k,
        )

    def index_documents(
        self,
        source: str | Path | list[Document],
        chunk_size: int = 512,
        chunk_overlap: int = 128,
    ) -> int:
        """Load (if path) and index documents into the vector store."""
        if isinstance(source, (str, Path)):
            documents = load_documents(source)
        else:
            documents = source

        chunks = chunk_documents(documents, chunk_size, chunk_overlap)
        vectors = self.retriever.embedder.embed([c.text for c in chunks])
        self.retriever.store.add(vectors, chunks)

        logger.info(
            "Indexed %d documents (%d chunks) into vector store",
            len(documents),
            len(chunks),
        )
        return len(chunks)

    def query(self, question: str, top_k: int | None = None) -> RAGResult:
        """Run the full RAG pipeline for a single question."""
        k = top_k or self.top_k

        results = self.retriever.retrieve(question, top_k=k)

        messages = build_prompt(
            question=question,
            results=results,
            conflict_aware=self.conflict_aware,
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
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run RAG pipeline")
    parser.add_argument("--config", default="configs/rag_base.yaml", help="Config YAML path")
    parser.add_argument("--docs", required=True, help="Path to documents to index")
    parser.add_argument("--question", required=True, help="Question to ask")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    pipeline = RAGPipeline.from_config(args.config)
    pipeline.index_documents(args.docs)
    result = pipeline.query(args.question)

    print(f"\nQuestion: {result.question}")
    print(f"\nAnswer: {result.answer}")
    print(f"\nSources:")
    for s in result.retrieved_sources:
        print(f"  - [{s['source']}] (score: {s['score']})")
