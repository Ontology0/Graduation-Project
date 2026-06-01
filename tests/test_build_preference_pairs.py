"""Unit tests for data/synthetic_conflicts/build_preference_pairs.py."""

from data.synthetic_conflicts.build_preference_pairs import (
    annotate_document_roles,
    filter_records_for_split,
    is_train_eligible,
    map_stance_to_role,
)


def test_map_stance_pilot_and_exp2_vocab():
    assert map_stance_to_role("current") == "authoritative"
    assert map_stance_to_role("outdated") == "contradicting"
    assert map_stance_to_role("true_doc") == "authoritative"
    assert map_stance_to_role("false_doc") == "contradicting"
    assert map_stance_to_role("distractor") == "distractor"


def test_annotate_document_roles():
    docs = [
        {"doc_id": "d1", "text": "a", "stance": "true_doc"},
        {"doc_id": "d2", "text": "b", "stance": "false_doc"},
    ]
    annotated = annotate_document_roles(docs)
    assert annotated[0]["role"] == "authoritative"
    assert annotated[1]["role"] == "contradicting"


def test_train_split_excludes_false_only_exp2_a():
    exp2_a = {
        "id": "A_01",
        "case_type": "A",
        "has_true_doc": False,
        "question": "q",
        "gold_answer": "g",
        "documents": [],
    }
    exp2_b = {
        "id": "B_01",
        "case_type": "B",
        "has_true_doc": True,
        "question": "q",
        "gold_answer": "g",
        "documents": [],
    }
    pilot_temporal = {
        "id": "case_001",
        "conflict_type": "temporal",
        "question": "q",
        "gold_answer": "g",
        "documents": [],
    }
    pilot_source_disagreement = {
        "id": "case_003",
        "conflict_type": "source_disagreement",
        "question": "q",
        "gold_answer": "g",
        "documents": [],
    }
    records = [exp2_a, exp2_b, pilot_temporal, pilot_source_disagreement]

    train = filter_records_for_split(records, "train")
    train_ids = {r["id"] for r in train}

    assert "A_01" not in train_ids
    assert "B_01" in train_ids
    assert "case_001" in train_ids
    assert "case_003" not in train_ids


def test_eval_split_includes_false_only():
    exp2_a = {
        "id": "A_01",
        "case_type": "A",
        "has_true_doc": False,
        "question": "q",
        "gold_answer": "g",
        "documents": [],
    }
    eval_records = filter_records_for_split([exp2_a], "eval")
    assert len(eval_records) == 1
    assert is_train_eligible(exp2_a) is False
