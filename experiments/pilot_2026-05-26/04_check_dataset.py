import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from collections import Counter

with open("data/synthetic_conflicts/pilot_conflicts.jsonl", encoding="utf-8") as f:
    cases = [json.loads(line) for line in f if line.strip()]

print(f"Total: {len(cases)}")
print(f"Conflict types: {Counter(c['conflict_type'] for c in cases)}")

required = {"id", "question", "gold_answer", "conflict_type", "documents"}
for c in cases:
    missing = required - c.keys()
    assert not missing, f"{c.get('id')}: missing {missing}"

    stances = Counter(d["stance"] for d in c["documents"])
    print(f"{c['id']}: docs={len(c['documents'])}, stances={dict(stances)}")

    assert stances["outdated"] >= 1, f"{c['id']}: no outdated"
    assert stances["current"] >= 1, f"{c['id']}: no current"

print("\nAll checks passed.")
