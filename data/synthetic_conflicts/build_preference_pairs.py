"""Build DPO preference pairs from conflict JSONL sources (scaffold)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Pilot (current/outdated/distractor) and exp2 (true_doc/false_doc/distractor).
STANCE_TO_ROLE: dict[str, str] = {
    "current": "authoritative",
    "true_doc": "authoritative",
    "outdated": "contradicting",
    "false_doc": "contradicting",
    "distractor": "distractor",
}


def map_stance_to_role(stance: str) -> str:
    """Map source stance label to normalized document role."""
    try:
        return STANCE_TO_ROLE[stance]
    except KeyError as exc:
        raise ValueError(f"Unknown stance: {stance!r}") from exc


def annotate_document_roles(documents: list[dict]) -> list[dict]:
    """Return documents with an added ``role`` field from ``stance``."""
    annotated: list[dict] = []
    for doc in documents:
        doc_copy = dict(doc)
        doc_copy["role"] = map_stance_to_role(doc["stance"])
        annotated.append(doc_copy)
    return annotated


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert conflict JSONL to preference pairs.")
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Input conflict JSONL path (repeatable).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for preference_pairs_{split}.jsonl output.",
    )
    parser.add_argument(
        "--split",
        choices=("train", "eval"),
        required=True,
        help="Split name for output file and filtering (logic added in later commits).",
    )
    args = parser.parse_args()

    for input_path in args.input:
        read_jsonl(Path(input_path))

    output_path = Path(args.output_dir) / f"preference_pairs_{args.split}.jsonl"
    write_jsonl(output_path, [])


if __name__ == "__main__":
    main()
