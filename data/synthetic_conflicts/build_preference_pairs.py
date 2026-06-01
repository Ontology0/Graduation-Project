"""Build DPO preference pairs from conflict JSONL sources (scaffold)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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
