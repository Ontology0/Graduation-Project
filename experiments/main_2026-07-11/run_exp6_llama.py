#!/usr/bin/env python3
"""exp6: closed-book confidence / entropy (Llama-3.1-8B).

Context is never injected. Step (1): load + hash + scoring (+ --dry-run).
Inference / AUROC / figures land in later steps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import string
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths & integrity
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "shared_data" / "exp6_questions_n400_seed42.jsonl"
EXPECTED_SHA256 = "963aa84bfb04b5f1fea2295c5e4ff9744e8a287899a0d9eb154c9467c92ac920"

RESULTS_DIR = HERE / "results"
FIGURES_DIR = HERE / "figures"
RESULTS_JSONL = RESULTS_DIR / "exp6_llama_results.jsonl"
SUMMARY_JSON = RESULTS_DIR / "exp6_llama_summary.json"
HIST_PNG = FIGURES_DIR / "exp6_llama_entropy_hist.png"

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS = 64

_ARTICLES = {"a", "an", "the"}
_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


# ---------------------------------------------------------------------------
# (1) Data load + hash + scoring
# ---------------------------------------------------------------------------


def load_and_verify(path: Path = DATA_PATH) -> list[dict]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, (
        f"데이터 버전 불일치!\n  got:      {digest}\n  expected: {EXPECTED_SHA256}"
    )
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    assert len(rows) == 400, f"expected 400 rows, got {len(rows)}"
    print(f"데이터 검증 OK  n={len(rows)}  sha256={digest[:12]}…")
    return rows


def source_label(row: dict) -> str:
    """Map raw provenance string / id prefix → CB | TQA."""
    sid = row.get("id", "")
    if sid.startswith("cbq_"):
        return "CB"
    if sid.startswith("tqa_"):
        return "TQA"
    src = row.get("source", "")
    if "CB_qa" in src or "cbqa" in src.lower():
        return "CB"
    if "trivia_qa" in src.lower() or "trivia" in src.lower():
        return "TQA"
    raise ValueError(f"unknown source for id={sid!r}: {src!r}")


def normalize(text: str) -> str:
    """Lowercase, strip punctuation & articles, collapse whitespace."""
    text = text.lower().translate(_PUNCT_TABLE)
    tokens = [t for t in text.split() if t not in _ARTICLES]
    return " ".join(tokens)


def score_answer(output: str, gold: str, aliases: list[str] | None = None) -> tuple[bool, str | None]:
    """Substring match after normalize.

    correct if any of (gold + aliases) appears inside normalized output.
    Returns (correct, matched) where matched is the original candidate string
    that hit (for manual review of short-alias false positives).
    """
    norm_out = normalize(output)
    candidates: list[str] = [gold] + list(aliases or [])
    for cand in candidates:
        if not cand:
            continue
        norm_cand = normalize(cand)
        if not norm_cand:
            continue
        if norm_cand in norm_out:
            return True, cand
    return False, None


def make_record(
    row: dict,
    output: str,
    entropy: float,
) -> dict:
    correct, matched = score_answer(output, row["gold"], row.get("aliases") or [])
    return {
        "id": row["id"],
        "source": source_label(row),
        "question": row["question"],
        "gold": row["gold"],
        "output": output,
        "entropy": entropy,
        "correct": correct,
        "matched": matched,
    }


# ---------------------------------------------------------------------------
# (1) dry-run: mock outputs to exercise load / hash / scoring
# ---------------------------------------------------------------------------


def _mock_rows_for_dry_run(rows: list[dict]) -> list[dict]:
    """Pick a few real rows and invent outputs that stress the scorer."""
    by_id = {r["id"]: r for r in rows}
    # CB: empty aliases, gold only
    cb = by_id["cbq_000"]  # gold: American Book Awards
    # TQA: many aliases; short gold "K" is a known FP risk (tqa_003)
    tqa_short = by_id["tqa_003"]
    tqa_ok = by_id["tqa_000"]  # gold: St. Basil's

    mocks = [
        # exact gold (CB)
        (cb, "American Book Awards", 0.12),
        # punctuation / article noise still matches
        (cb, "The answer is the American Book Awards.", 0.20),
        # wrong (CB)
        (cb, "Pulitzer Prize", 0.85),
        # TQA gold match
        (tqa_ok, "St. Basil's Cathedral in Moscow.", 0.18),
        # TQA alias match (should record matched=alias, not gold)
        (tqa_ok, "It is also called Pokhrovsky Cathedral.", 0.22),
        # short-gold substring FP risk: gold "K" inside "known" / "Moscow" etc.
        (tqa_short, "I do not know the answer.", 0.90),
        # genuine short-gold hit
        (tqa_short, "K", 0.15),
    ]
    return [make_record(row, out, ent) for row, out, ent in mocks]


def run_dry_run() -> list[dict]:
    rows = load_and_verify()
    records = _mock_rows_for_dry_run(rows)
    print("\n--- dry-run scoring ---")
    for rec in records:
        flag = "✓" if rec["correct"] else "✗"
        print(
            f"[{flag}] {rec['id']:8s}  source={rec['source']:3s}  "
            f"matched={rec['matched']!r}\n"
            f"         gold={rec['gold']!r}\n"
            f"         out ={rec['output']!r}\n"
            f"         H   ={rec['entropy']:.3f}"
        )
    n_correct = sum(1 for r in records if r["correct"])
    print(f"\ndry-run: {n_correct}/{len(records)} marked correct "
          f"(inspect short-gold matched= values for false positives)")
    return records


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="exp6 Llama closed-book entropy runner")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip model; mock 2–3 outputs to verify load/hash/scoring.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run:
        run_dry_run()
        print("\n[step 1 OK] load + hash + scoring. "
              "Inference / AUROC / figures not wired yet.")
        return

    # Steps (2)–(3) will go here.
    raise SystemExit(
        "Full inference not implemented yet. "
        "Use --dry-run for step-1 checks, or wait for steps 2–3."
    )


if __name__ == "__main__":
    main()
