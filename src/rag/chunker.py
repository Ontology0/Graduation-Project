"""Split documents into smaller chunks for embedding and retrieval."""

from __future__ import annotations

from dataclasses import replace
from typing import Sequence

from src.rag.document_loader import Document


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 128,
) -> list[str]:
    """Split *text* into overlapping windows of roughly *chunk_size* characters.

    Tries to break on sentence boundaries (". ") when possible so chunks
    are more semantically coherent.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be in [0, chunk_size)")

    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks: list[str] = []
    start = 0
    min_chunk_chars = max(120, chunk_size // 3)
    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            boundary = text.rfind(". ", start, end)
            # Only snap to a boundary when it doesn't create tiny chunks,
            # otherwise overlap logic can degrade into 1-char sliding windows.
            if boundary != -1 and (boundary - start) >= min_chunk_chars:
                end = boundary + 2  # include the period and space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        next_start = end - chunk_overlap
        if next_start <= start:
            next_start = min(start + min_chunk_chars, len(text))
        start = next_start

    return chunks


def chunk_documents(
    documents: Sequence[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 128,
) -> list[Document]:
    """Split each document into chunk-level Document objects.

    Each chunk inherits the parent document's metadata, with added
    ``chunk_index`` and ``original_source`` fields.
    """
    chunked: list[Document] = []
    for doc in documents:
        pieces = chunk_text(doc.text, chunk_size, chunk_overlap)
        for i, piece in enumerate(pieces):
            meta = {
                **doc.metadata,
                "chunk_index": i,
                "total_chunks": len(pieces),
                "original_source": doc.source,
            }
            chunked.append(
                replace(doc, text=piece, source=f"{doc.source}#chunk{i}", metadata=meta)
            )
    return chunked
