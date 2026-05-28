"""Load synthetic conflict pilot cases for batch RAG runs."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.rag.config import resolve_path
from src.rag.document_loader import Document


def load_conflict_dataset(path: str | Path, limit: int | None = None) -> list[dict[str, Any]]:
    """Load pilot / synthetic conflict cases from JSONL (one object per line)."""
    path = resolve_path(path)
    cases: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}") from e
            if limit is not None and len(cases) >= limit:
                break
    if not cases:
        raise ValueError(f"No cases loaded from {path}")
    return cases


def documents_from_case(case: dict[str, Any]) -> list[Document]:
    """Map pilot ``documents[]`` entries to :class:`Document` for indexing."""
    case_id = str(case.get("id", "unknown"))
    raw_docs = case.get("documents")
    if not raw_docs:
        raise ValueError(f"Case {case_id} has no documents")

    documents: list[Document] = []
    for entry in raw_docs:
        doc_id = str(entry.get("doc_id", len(documents)))
        text = entry.get("text", "")
        if not text.strip():
            raise ValueError(f"Case {case_id} document {doc_id} has empty text")
        documents.append(
            Document(
                text=text,
                source=f"{case_id}/{doc_id}",
                metadata={
                    "case_id": case_id,
                    "doc_id": doc_id,
                    "stance": entry.get("stance", ""),
                },
            )
        )
    return documents


def _safe_experiment_dir(name: str) -> str:
    safe = re.sub(r"[^\w.\-]+", "_", name.strip())
    return safe or "unknown_experiment"


def batch_output_path(
    output_dir: Path,
    experiment_name: str,
    dataset_path: Path,
) -> Path:
    """``outputs/{experiment_name}/{dataset_stem}_{timestamp}.jsonl``"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    stem = dataset_path.stem
    return output_dir / _safe_experiment_dir(experiment_name) / f"{stem}_{timestamp}.jsonl"
