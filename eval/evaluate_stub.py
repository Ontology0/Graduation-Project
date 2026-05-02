"""Evaluation placeholder: interface only; no scores are computed."""

from __future__ import annotations


def evaluate_placeholder(prediction: str, reference: str | None = None) -> dict:
    """
    Reserved signature for future metrics.

    Does not compute real scores; metrics stay empty until eval is implemented.
    """
    # Placeholder: do not compute or fabricate scores.
    _ = (prediction, reference)  # accepted for API stability; unused
    return {
        "status": "not_implemented",
        "metrics": {},
    }


if __name__ == "__main__":
    print(evaluate_placeholder("pred text", "ref text"))
