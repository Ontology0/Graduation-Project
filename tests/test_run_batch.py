"""Unit tests for pilot dataset helpers and batch output paths."""

from pathlib import Path

from src.rag.pilot_dataset import (
    batch_output_path,
    documents_from_case,
    load_conflict_dataset,
)


def test_load_conflict_dataset_limit():
    path = Path("data/synthetic_conflicts/pilot_conflicts.jsonl")
    cases = load_conflict_dataset(path, limit=2)
    assert len(cases) == 2
    assert cases[0]["id"] == "case_001"


def test_documents_from_case():
    cases = load_conflict_dataset(
        "data/synthetic_conflicts/pilot_conflicts.jsonl", limit=1
    )
    docs = documents_from_case(cases[0])
    assert len(docs) >= 3
    assert docs[0].source.startswith("case_001/")
    assert docs[0].metadata["stance"] in ("outdated", "current", "distractor")


def test_output_path():
    out = batch_output_path(
        Path("outputs"),
        "base_rag",
        Path("data/synthetic_conflicts/pilot_conflicts.jsonl"),
    )
    assert out.parent.name == "base_rag"
    assert out.name.startswith("pilot_conflicts_")
    assert out.suffix == ".jsonl"
