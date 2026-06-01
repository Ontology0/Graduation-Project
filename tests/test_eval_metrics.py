"""Unit tests for evaluation metrics (issue #56)."""

from src.evaluation.evaluate import (
    aggregate_by_case_type,
    annotate_scoring_fields,
    build_capability_map,
    conflict_resolution_accuracy,
    contains_target,
    detects_abstention,
    false_doc_follow_rate,
    abstention_rate,
    metrics_for_rows,
)


def test_contains_target_substring_and_tokens():
    assert contains_target("The capital is Canberra.", "Canberra")
    assert contains_target("Au is the symbol for gold", "Au")
    assert not contains_target("Sydney is the capital", "Canberra")


def test_conflict_resolution_accuracy():
    rows = [
        {"true_hit": True},
        {"true_hit": False},
        {"true_hit": True},
    ]
    assert conflict_resolution_accuracy(rows) == 2 / 3


def test_false_doc_follow_rate():
    rows = [
        {"false_answer": "Sydney", "false_follow_only": True},
        {"false_answer": "Sydney", "false_follow_only": False},
        {"false_answer": "", "false_follow_only": False},
    ]
    assert false_doc_follow_rate(rows) == 0.5


def test_abstention_rate():
    rows = [{"abstention": True}, {"abstention": False}, {"abstention": True}]
    assert abstention_rate(rows) == 2 / 3
    assert detects_abstention("I am uncertain about the answer.")


def test_annotate_scoring_fields():
    row = annotate_scoring_fields(
        {
            "predicted_answer": "The answer is Canberra, not Sydney.",
            "gold_answer": "Canberra",
            "false_answer": "Sydney",
        }
    )
    assert row["true_hit"] is True
    assert row["false_hit"] is True
    assert row["correct"] is True
    assert row["false_follow_only"] is False


def test_aggregate_by_case_type_and_capability_map():
    rows = [
        {"case_type": "A", "true_hit": True, "false_answer": "x", "false_follow_only": False, "abstention": False},
        {"case_type": "A", "true_hit": False, "false_answer": "x", "false_follow_only": True, "abstention": False},
        {"case_type": "B", "true_hit": True, "false_answer": "y", "false_follow_only": False, "abstention": False},
        {"case_type": "B", "true_hit": True, "false_answer": "y", "false_follow_only": False, "abstention": False},
    ]
    by_type = aggregate_by_case_type(rows)
    assert by_type["A"]["count"] == 2.0
    assert by_type["A"]["conflict_resolution_accuracy"] == 0.5
    assert by_type["B"]["conflict_resolution_accuracy"] == 1.0

    capability = build_capability_map(by_type)
    assert capability["A"] == "partial"
    assert capability["B"] == "handled"

    overall = metrics_for_rows(rows)
    assert overall["count"] == 4.0
    assert overall["conflict_resolution_accuracy"] == 0.75
