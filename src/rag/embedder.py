"""Generate dense vector embeddings using sentence-transformers."""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    """Thin wrapper around a SentenceTransformer model for embedding text."""

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str | None = None):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)
        self._dim: int | None = None
        logger.info("Loaded embedding model: %s", model_name)

    @property
    def dimension(self) -> int:
        if self._dim is None:
            probe = self.model.encode(["dim probe"], convert_to_numpy=True)
            self._dim = probe.shape[1]
        return self._dim

    def embed(self, texts: Sequence[str], batch_size: int = 64) -> np.ndarray:
        """Return (N, D) float32 embeddings for *texts*."""
        vectors = self.model.encode(
            list(texts),
            batch_size=batch_size,
            show_progress_bar=len(texts) > batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return vectors.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string. Returns shape (D,)."""
        return self.embed([query])[0]
