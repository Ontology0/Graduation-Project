#!/usr/bin/env python3
"""Validate preference-pair JSONL lines against data/schema/preference_pair.schema.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "data" / "schema" / "preference_pair.schema.json"


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _validate_types(record: dict, schema: dict, errors: list[str]) -> None:
    properties = schema.get("properties", {})
    for key, spec in properties.items():
        if key not in record:
            continue
        expected = spec.get("type")
        if expected == "string" and not isinstance(record[key], str):
            errors.append(f"{key}: expected string")
        elif expected == "object" and not isinstance(record[key], dict):
            errors.append(f"{key}: expected object")


def validate_record(record: dict, schema: dict) -> list[str]:
    """Validate one record; return a list of error messages."""
    errors: list[str] = []

    if schema.get("type") == "object" and not isinstance(record, dict):
        return ["record must be a JSON object"]

    for field in schema.get("required", []):
        if field not in record:
            errors.append(f"missing required field: {field}")

    if schema.get("additionalProperties") is False:
        allowed = set(schema.get("properties", {}).keys())
        for key in record:
            if key not in allowed:
                errors.append(f"additional property not allowed: {key}")

    _validate_types(record, schema, errors)
    return errors


def validate_jsonl(path: Path, schema: dict) -> int:
    """Validate all lines; return count of invalid lines."""
    failures = 0
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                failures += 1
                print(f"{path}:{line_no}: invalid JSON: {exc}", file=sys.stderr)
                continue

            errors = validate_record(record, schema)
            if errors:
                failures += 1
                for err in errors:
                    print(f"{path}:{line_no}: {err}", file=sys.stderr)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate preference pair JSONL files.")
    parser.add_argument("paths", nargs="+", help="JSONL file paths to validate.")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help="Path to preference_pair JSON Schema.",
    )
    args = parser.parse_args()

    schema = load_schema(Path(args.schema))
    total_failures = 0
    for path_str in args.paths:
        total_failures += validate_jsonl(Path(path_str), schema)

    return 1 if total_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
