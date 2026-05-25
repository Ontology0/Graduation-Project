"""FAISS-backed vector store for dense retrieval."""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Sequence

import faiss
import numpy as np

from src.rag.document_loader import Document

logger = logging.getLogger(__name__)


class FaissVectorStore:
    """In-memory FAISS index with document metadata bookkeeping.

    Uses Inner Product (IP) index, which is equivalent to cosine similarity
    when vectors are L2-normalized (as produced by Embedder).
    """

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self._documents: list[Document] = []

    @property
    def size(self) -> int:
        return self.index.ntotal

    def add(self, vectors: np.ndarray, documents: Sequence[Document]) -> None:
        """Add vectors and their corresponding documents to the store."""
        if len(vectors) != len(documents):
            raise ValueError(
                f"Vector count ({len(vectors)}) != document count ({len(documents)})"
            )
        vectors = np.ascontiguousarray(vectors, dtype=np.float32)
        self.index.add(vectors)
        self._documents.extend(documents)
        logger.info("Added %d vectors (total: %d)", len(vectors), self.size)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[Document, float]]:
        """Return the top-k most similar documents with their scores."""
        if self.size == 0:
            return []

        top_k = min(top_k, self.size)
        query_vector = np.ascontiguousarray(
            query_vector.reshape(1, -1), dtype=np.float32
        )
        scores, indices = self.index.search(query_vector, top_k)

        results: list[tuple[Document, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self._documents[idx], float(score)))
        return results

    def save(self, directory: str | Path) -> None:
        """Persist the FAISS index and document metadata to disk."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(directory / "index.faiss"))
        with open(directory / "documents.pkl", "wb") as f:
            pickle.dump(self._documents, f)
        logger.info("Saved vector store to %s (%d vectors)", directory, self.size)

    @classmethod
    def load(cls, directory: str | Path) -> FaissVectorStore:
        """Load a previously saved vector store from disk."""
        directory = Path(directory)
        index = faiss.read_index(str(directory / "index.faiss"))

        with open(directory / "documents.pkl", "rb") as f:
            documents = pickle.load(f)

        store = cls(dimension=index.d)
        store.index = index
        store._documents = documents
        logger.info("Loaded vector store from %s (%d vectors)", directory, store.size)
        return store
