"""Generate dense vector embeddings.

Supports:
- SentenceTransformers (local): e.g. `sentence-transformers/all-MiniLM-L6-v2`
- OpenAI embeddings (API): prefix with `openai/`, e.g. `openai/text-embedding-3-small`
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np

from src.rag.config import get_api_key

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _is_openai_model(name: str) -> bool:
    return (name or "").lower().startswith("openai/")


class Embedder:
    """Embedding backend wrapper (SentenceTransformers or OpenAI)."""

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str | None = None):
        self.model_name = model_name
        self._dim: int | None = None

        if _is_openai_model(model_name):
            try:
                from openai import OpenAI  # type: ignore
            except Exception as e:  # pragma: no cover
                raise ImportError(
                    "openai package is required for OpenAI embeddings. "
                    "Install it (e.g. `pip install openai`)."
                ) from e

            self._openai_model = model_name.split("/", 1)[1]
            self._openai = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
            self.model = None
            logger.info("Using OpenAI embedding model: %s", self._openai_model)
        else:
            from sentence_transformers import SentenceTransformer

            self._openai_model = None
            self._openai = None
            self.model = SentenceTransformer(model_name, device=device)
            logger.info("Loaded embedding model: %s", model_name)

    @property
    def _uses_e5_prefix(self) -> bool:
        name = (self.model_name or "").lower()
        return "e5" in name

    def _prep_passage(self, text: str) -> str:
        t = (text or "").strip()
        if self._uses_e5_prefix:
            return f"passage: {t}"
        return t

    def _prep_query(self, query: str) -> str:
        q = (query or "").strip()
        if self._uses_e5_prefix:
            return f"query: {q}"
        return q

    @property
    def dimension(self) -> int:
        if self._dim is None:
            if self._openai is not None:
                resp = self._openai.embeddings.create(
                    model=self._openai_model,
                    input=["dim probe"],
                )
                self._dim = len(resp.data[0].embedding)
            else:
                probe = self.model.encode(["dim probe"], convert_to_numpy=True)
                self._dim = probe.shape[1]
        return self._dim

    def embed(self, texts: Sequence[str], batch_size: int = 64) -> np.ndarray:
        """Return (N, D) float32 embeddings for *texts*."""
        if self._openai is not None:
            inputs = [t.strip() for t in texts]
            out: list[list[float]] = []
            for i in range(0, len(inputs), batch_size):
                chunk = inputs[i : i + batch_size]
                resp = self._openai.embeddings.create(model=self._openai_model, input=chunk)
                out.extend([d.embedding for d in resp.data])
            vectors = np.asarray(out, dtype=np.float32)
            norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
            return (vectors / norms).astype(np.float32)

        prepared = [self._prep_passage(t) for t in texts]
        vectors = self.model.encode(
            prepared,
            batch_size=batch_size,
            show_progress_bar=len(texts) > batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return vectors.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string. Returns shape (D,)."""
        if self._openai is not None:
            resp = self._openai.embeddings.create(
                model=self._openai_model,
                input=[query.strip()],
            )
            vec = np.asarray(resp.data[0].embedding, dtype=np.float32)
            vec = vec / (np.linalg.norm(vec) + 1e-12)
            return vec.astype(np.float32)

        prepared = self._prep_query(query)
        vectors = self.model.encode(
            [prepared],
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return vectors.astype(np.float32)[0]
