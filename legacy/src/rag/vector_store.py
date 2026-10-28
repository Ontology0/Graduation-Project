"""Vector store backends for dense retrieval.

Default backend is FAISS when available, with a NumPy fallback for environments
where FAISS wheels are unavailable.
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Protocol, Sequence, runtime_checkable

import numpy as np

from src.rag.document_loader import Document

logger = logging.getLogger(__name__)

try:
    import faiss  # type: ignore

    _HAS_FAISS = True
except Exception:  # pragma: no cover
    faiss = None  # type: ignore
    _HAS_FAISS = False


@runtime_checkable
class VectorStore(Protocol):
    dimension: int

    def add(self, vectors: np.ndarray, documents: Sequence[Document]) -> None: ...

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[Document, float]]: ...


class FaissVectorStore:
    """In-memory FAISS index with document metadata bookkeeping.

    Uses Inner Product (IP) index, which is equivalent to cosine similarity
    when vectors are L2-normalized (as produced by Embedder).
    """

    def __init__(self, dimension: int):
        if not _HAS_FAISS:  # pragma: no cover
            raise ImportError(
                "faiss is not installed. Install faiss-cpu (or use retrieval.backend: numpy)."
            )
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


class NumpyVectorStore:
    """Simple in-memory vector store using NumPy dot-product search.

    Assumes vectors are L2-normalized so dot-product equals cosine similarity.
    """

    def __init__(self, dimension: int):
        self.dimension = int(dimension)
        self._vectors: np.ndarray | None = None  # shape (N, D), float32
        self._documents: list[Document] = []

    @property
    def size(self) -> int:
        return 0 if self._vectors is None else int(self._vectors.shape[0])

    def add(self, vectors: np.ndarray, documents: Sequence[Document]) -> None:
        if len(vectors) != len(documents):
            raise ValueError(
                f"Vector count ({len(vectors)}) != document count ({len(documents)})"
            )
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected vectors shape (N, {self.dimension}), got {tuple(vectors.shape)}"
            )
        vectors = np.ascontiguousarray(vectors)

        if self._vectors is None:
            self._vectors = vectors
        else:
            self._vectors = np.vstack([self._vectors, vectors])
        self._documents.extend(documents)
        logger.info("Added %d vectors (total: %d)", len(vectors), self.size)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[Document, float]]:
        if self._vectors is None or not self._documents:
            return []
        q = np.asarray(query_vector, dtype=np.float32).reshape(-1)
        if q.shape[0] != self.dimension:
            raise ValueError(f"Expected query shape ({self.dimension},), got {tuple(q.shape)}")

        scores = self._vectors @ q  # (N,)
        k = min(int(top_k), int(scores.shape[0]))
        if k <= 0:
            return []
        idx = np.argpartition(-scores, kth=k - 1)[:k]
        idx = idx[np.argsort(-scores[idx])]
        return [(self._documents[int(i)], float(scores[int(i)])) for i in idx]

    def save(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        if self._vectors is None:
            vectors = np.zeros((0, self.dimension), dtype=np.float32)
        else:
            vectors = self._vectors
        np.save(directory / "vectors.npy", vectors)
        with open(directory / "documents.pkl", "wb") as f:
            pickle.dump(self._documents, f)
        logger.info("Saved numpy vector store to %s (%d vectors)", directory, self.size)

    @classmethod
    def load(cls, directory: str | Path) -> "NumpyVectorStore":
        directory = Path(directory)
        vectors = np.load(directory / "vectors.npy")
        with open(directory / "documents.pkl", "rb") as f:
            documents = pickle.load(f)
        store = cls(dimension=int(vectors.shape[1]) if vectors.ndim == 2 else 0)
        store._vectors = vectors.astype(np.float32, copy=False)
        store._documents = documents
        logger.info("Loaded numpy vector store from %s (%d vectors)", directory, store.size)
        return store


def make_vector_store(backend: str, dimension: int) -> VectorStore:
    backend = (backend or "faiss").lower()
    if backend == "faiss":
        if _HAS_FAISS:
            return FaissVectorStore(dimension=dimension)
        logger.warning("FAISS not available; falling back to NumPy vector store.")
        return NumpyVectorStore(dimension=dimension)
    if backend in ("numpy", "bruteforce"):
        return NumpyVectorStore(dimension=dimension)
    raise ValueError(f"Unknown retrieval backend: {backend}")


def load_vector_store(backend: str, directory: str | Path) -> VectorStore:
    backend = (backend or "faiss").lower()
    if backend == "faiss":
        if not _HAS_FAISS:
            raise ImportError(
                "faiss is not installed, cannot load a faiss index. "
                "Install faiss-cpu or use retrieval.backend: numpy and rebuild index."
            )
        return FaissVectorStore.load(directory)
    if backend in ("numpy", "bruteforce"):
        return NumpyVectorStore.load(directory)
    raise ValueError(f"Unknown retrieval backend: {backend}")


def save_vector_store(store: VectorStore, directory: str | Path) -> None:
    if hasattr(store, "save"):
        store.save(directory)  # type: ignore[attr-defined]
        return
    raise TypeError(f"Vector store does not support save(): {type(store).__name__}")
