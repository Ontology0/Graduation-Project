"""Tests for preference pair schema validation."""

import json
from pathlib import Path

from scripts.validate_preference_data import load_schema, validate_record

SCHEMA_PATH = Path("data/schema/preference_pair.schema.json")


def test_sample_pair_passes_schema():
    schema = load_schema(SCHEMA_PATH)
    sample = {
        "id": "test_pair_001",
        "prompt": "### system\nYou are helpful.\n\n### user\nContext:\n[d1:current]\nFact.",
        "chosen": "Answer: gold\nCitation: [d1:current]",
        "rejected": "Answer: wrong\nCitation: [d2:outdated]",
        "metadata": {
            "conflict_type": "context-memory",
            "resolution_rule": "Prefer current over outdated.",
            "original_subtype": "temporal",
        },
    }
    errors = validate_record(sample, schema)
    assert errors == []


def test_missing_required_field_fails():
    schema = load_schema(SCHEMA_PATH)
    incomplete = {
        "id": "x",
        "prompt": "p",
        "chosen": "c",
    }
    errors = validate_record(incomplete, schema)
    assert any("rejected" in err for err in errors)


def test_schema_file_is_valid_json():
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        json.load(handle)
