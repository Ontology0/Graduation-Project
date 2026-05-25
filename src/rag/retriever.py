"""Retriever: query-to-document search combining Embedder and VectorStore."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence

from src.rag.chunker import chunk_documents
from src.rag.document_loader import Document
from src.rag.embedder import Embedder
from src.rag.vector_store import FaissVectorStore

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """A single retrieved chunk with its similarity score."""

    document: Document
    score: float

    @property
    def text(self) -> str:
        return self.document.text

    @property
    def source(self) -> str:
        return self.document.source


class Retriever:
    """End-to-end retriever: embeds a query, searches the vector store,
    and returns ranked document chunks."""

    def __init__(
        self,
        embedder: Embedder,
        store: FaissVectorStore,
        top_k: int = 5,
    ):
        self.embedder = embedder
        self.store = store
        self.top_k = top_k

    @classmethod
    def build_from_documents(
        cls,
        documents: Sequence[Document],
        embedder: Embedder,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        top_k: int = 5,
    ) -> Retriever:
        """Chunk, embed, and index documents in one step."""
        chunks = chunk_documents(documents, chunk_size, chunk_overlap)
        logger.info("Chunked %d documents into %d chunks", len(documents), len(chunks))

        texts = [c.text for c in chunks]
        vectors = embedder.embed(texts)

        store = FaissVectorStore(dimension=embedder.dimension)
        store.add(vectors, chunks)
        return cls(embedder=embedder, store=store, top_k=top_k)

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievalResult]:
        """Embed *query* and return the top-k most relevant chunks."""
        k = top_k or self.top_k
        query_vec = self.embedder.embed_query(query)
        hits = self.store.search(query_vec, top_k=k)
        results = [RetrievalResult(document=doc, score=score) for doc, score in hits]
        logger.info("Retrieved %d chunks for query: %.60s...", len(results), query)
        return results
