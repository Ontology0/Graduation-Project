import json
from pathlib import Path


def test_schema_files_are_valid_json():
    for path in Path("data/schema").glob("*.json"):
        with open(path, encoding="utf-8") as f:
            json.load(f)
