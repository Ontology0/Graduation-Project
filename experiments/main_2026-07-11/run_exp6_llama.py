#!/usr/bin/env python3
"""exp6: closed-book confidence / entropy (Llama-3.1-8B).

Context is never injected.
  (1) load + hash + scoring (+ --dry-run)
  (2) generate_with_entropy + resume JSONL
  (3) --analyze: AUROC / histogram / summary (no model)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import string
import warnings
from pathlib import Path
from typing import Any

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
HIST_PNG_TQA = FIGURES_DIR / "exp6_llama_entropy_hist_tqa.png"

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


def normalize(text: str) -> list[str]:
    """Lowercase, strip punctuation & articles → token list."""
    text = text.lower().translate(_PUNCT_TABLE)
    return [t for t in text.split() if t not in _ARTICLES]


def _is_contiguous_subsequence(needle: list[str], haystack: list[str]) -> bool:
    """True if needle is a contiguous token span inside haystack."""
    n, m = len(needle), len(haystack)
    if n == 0 or n > m:
        return False
    for i in range(m - n + 1):
        if haystack[i : i + n] == needle:
            return True
    return False


def score_answer(output: str, gold: str, aliases: list[str] | None = None) -> tuple[bool, str | None]:
    """Whole-token contiguous subsequence match after normalize.

    correct if any of (gold + aliases) token sequence appears as a contiguous
    span in the output tokens (avoids "K"∈"know", "Cat"∈"category" FPs).
    Returns (correct, matched) where matched is the original candidate string.
    """
    out_toks = normalize(output)
    candidates: list[str] = [gold] + list(aliases or [])
    for cand in candidates:
        if not cand:
            continue
        cand_toks = normalize(cand)
        if not cand_toks:
            continue
        if _is_contiguous_subsequence(cand_toks, out_toks):
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
        # short-gold token FP risk (must be ✗): "K" must not match inside "know"
        (tqa_short, "I do not know the answer.", 0.90),
        # genuine short-gold hit (whole token "K")
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
# (2) Inference (closed-book only) + resume JSONL
# ---------------------------------------------------------------------------


def load_done_ids(path: Path = RESULTS_JSONL) -> set[str]:
    if not path.exists():
        return set()
    done: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            done.add(json.loads(line)["id"])
    return done


def append_record(record: dict, path: Path = RESULTS_JSONL) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()


def load_model() -> tuple[Any, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading {MODEL_ID} (bfloat16, device_map=auto)…")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    n_params = sum(p.numel() for p in model.parameters()) / 1e9
    print(f"로드 완료. 파라미터 수: {n_params:.2f}B")
    return model, tokenizer


def generate_with_entropy(model: Any, tokenizer: Any, question: str) -> tuple[str, float]:
    """Closed-book generate + mean token Shannon entropy.

    Port of llama_pilot generate_with_entropy(context=None) only.
    Context is never accepted — parametric knowledge only.
    """
    import torch

    user = f"Answer the question concisely.\n\nQuestion: {question}"
    msgs = [{"role": "user", "content": user}]

    inputs = tokenizer.apply_chat_template(
        msgs,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    gen_ids = out.sequences[0][input_len:]
    text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

    ents: list[float] = []
    for logits in out.scores:
        p = torch.softmax(logits[0].float(), dim=-1)
        ent = -(p * torch.log(p + 1e-12)).sum().item()
        ents.append(ent)
    mean_entropy = float(sum(ents) / len(ents)) if ents else 0.0

    # Drop generation tensors so scores do not accumulate across cases.
    del out, gen_ids, inputs
    return text, mean_entropy


def run_inference(*, limit: int | None = None) -> None:
    from tqdm import tqdm

    rows = load_and_verify()
    if limit is not None:
        if limit < 1:
            raise SystemExit("--limit must be >= 1")
        rows = rows[:limit]
        print(f"--limit={limit}: running first {len(rows)} questions")

    done = load_done_ids(RESULTS_JSONL)
    if done:
        print(f"resume: {len(done)} ids already in {RESULTS_JSONL.name}")

    todo = [r for r in rows if r["id"] not in done]
    print(f"to generate: {len(todo)} / selected {len(rows)}")
    if not todo:
        print("nothing to do.")
        return

    model, tokenizer = load_model()
    n_ok = 0
    for row in tqdm(todo, desc="exp6-llama"):
        text, entropy = generate_with_entropy(model, tokenizer, row["question"])
        rec = make_record(row, text, entropy)
        append_record(rec)
        if rec["correct"]:
            n_ok += 1

    print(f"wrote {len(todo)} records → {RESULTS_JSONL}")
    print(f"this run correct: {n_ok}/{len(todo)}")


# ---------------------------------------------------------------------------
# (3) Analyze: AUROC / histogram / summary (no model)
# ---------------------------------------------------------------------------


def load_results(path: Path = RESULTS_JSONL) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"results not found: {path}\nRun inference first, or --dry-run.")
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    if not records:
        raise SystemExit(f"empty results file: {path}")
    return records


def _mean_or_none(xs: list[float]) -> float | None:
    return float(sum(xs) / len(xs)) if xs else None


def compute_metrics(records: list[dict]) -> dict[str, Any]:
    """Metrics for one group. AUROC / confidently_wrong → None when undefined."""
    n = len(records)
    if n == 0:
        return {
            "n": 0,
            "n_correct": 0,
            "accuracy": None,
            "auroc": None,
            "mean_entropy_correct": None,
            "mean_entropy_incorrect": None,
            "confidently_wrong_frac": None,
        }

    corrects = [bool(r["correct"]) for r in records]
    ents = [float(r["entropy"]) for r in records]
    n_correct = sum(corrects)
    n_incorrect = n - n_correct
    ok_ents = [e for e, c in zip(ents, corrects) if c]
    bad_ents = [e for e, c in zip(ents, corrects) if not c]

    # y_true=1 for incorrect; y_score=entropy → AUROC>0.5 means higher H predicts error
    auroc: float | None
    if n_correct == 0 or n_incorrect == 0:
        auroc = None
    else:
        from sklearn.metrics import roc_auc_score

        y_true = [0 if c else 1 for c in corrects]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            auroc = float(roc_auc_score(y_true, ents))

    if n_correct == 0:
        conf_wrong: float | None = None
    elif n_incorrect == 0:
        conf_wrong = 0.0
    else:
        med_ok = statistics.median(ok_ents)
        conf_wrong = float(sum(1 for e in bad_ents if e <= med_ok) / n_incorrect)

    return {
        "n": n,
        "n_correct": n_correct,
        "accuracy": float(n_correct / n),
        "auroc": auroc,
        "mean_entropy_correct": _mean_or_none(ok_ents),
        "mean_entropy_incorrect": _mean_or_none(bad_ents),
        "confidently_wrong_frac": conf_wrong,
    }


def build_summary(records: list[dict]) -> dict[str, Any]:
    by_src = {
        "all": records,
        "CB": [r for r in records if r.get("source") == "CB"],
        "TQA": [r for r in records if r.get("source") == "TQA"],
    }
    return {name: compute_metrics(group) for name, group in by_src.items()}


def plot_entropy_hist(records: list[dict], out_path: Path, *, title: str) -> bool:
    """Overlay correct vs incorrect entropy histograms. Returns False if skipped."""
    ok = [float(r["entropy"]) for r in records if r["correct"]]
    bad = [float(r["entropy"]) for r in records if not r["correct"]]
    if not ok and not bad:
        return False

    import matplotlib.pyplot as plt

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bins = 20
    if ok:
        ax.hist(ok, bins=bins, alpha=0.55, label=f"correct (n={len(ok)})", color="#2a9d8f")
    if bad:
        ax.hist(bad, bins=bins, alpha=0.55, label=f"incorrect (n={len(bad)})", color="#e76f51")
    ax.set_xlabel("mean token entropy")
    ax.set_ylabel("count")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return True


def print_summary_table(summary: dict[str, Any]) -> None:
    headers = (
        "group", "n", "n_ok", "acc", "auroc", "H_ok", "H_bad", "conf_wrong",
    )
    rows: list[list[str]] = []
    for name in ("all", "CB", "TQA"):
        m = summary[name]

        def fmt(x: Any, nd: int = 3) -> str:
            if x is None:
                return "None"
            if isinstance(x, float):
                return f"{x:.{nd}f}"
            return str(x)

        rows.append([
            name,
            str(m["n"]),
            str(m["n_correct"]),
            fmt(m["accuracy"]),
            fmt(m["auroc"]),
            fmt(m["mean_entropy_correct"]),
            fmt(m["mean_entropy_incorrect"]),
            fmt(m["confidently_wrong_frac"]),
        ])

    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) for i in range(len(headers))]

    def line(cells: list[str]) -> str:
        return "  ".join(c.ljust(widths[i]) for i, c in enumerate(cells))

    print("\n--- exp6 summary ---")
    print(line(list(headers)))
    print(line(["-" * w for w in widths]))
    for r in rows:
        print(line(r))
    print("(AUROC: y=incorrect, score=entropy; >0.5 ⇒ higher entropy predicts error)")


def run_analyze(
    records: list[dict] | None = None,
    *,
    results_path: Path = RESULTS_JSONL,
    summary_path: Path = SUMMARY_JSON,
    hist_path: Path = HIST_PNG,
    hist_tqa_path: Path = HIST_PNG_TQA,
) -> dict[str, Any]:
    if records is None:
        records = load_results(results_path)
        print(f"analyze n={len(records)} from {results_path}")
    else:
        print(f"analyze n={len(records)} (in-memory)")

    summary = build_summary(records)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {summary_path}")

    if plot_entropy_hist(
        records, hist_path, title="exp6 Llama: entropy (correct vs incorrect)"
    ):
        print(f"wrote {hist_path}")

    tqa = [r for r in records if r.get("source") == "TQA"]
    if tqa and any(r["correct"] for r in tqa):
        if plot_entropy_hist(
            tqa, hist_tqa_path, title="exp6 Llama TQA: entropy (correct vs incorrect)"
        ):
            print(f"wrote {hist_tqa_path}")

    print_summary_table(summary)
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="exp6 Llama closed-book entropy runner")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip model; mock outputs to verify load/hash/scoring/analyze.",
    )
    p.add_argument(
        "--analyze",
        action="store_true",
        help="Skip model; compute AUROC/summary/plots from results JSONL.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Run only the first N questions (smoke test).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run:
        records = run_dry_run()
        # Exercise analyze path on mocks without clobbering real Colab outputs.
        run_analyze(
            records,
            summary_path=RESULTS_DIR / "exp6_llama_summary_dryrun.json",
            hist_path=FIGURES_DIR / "exp6_llama_entropy_hist_dryrun.png",
            hist_tqa_path=FIGURES_DIR / "exp6_llama_entropy_hist_tqa_dryrun.png",
        )
        print("\n[dry-run OK] load + hash + scoring + analyze (no model).")
        return

    if args.analyze:
        run_analyze()
        print("\n[analyze OK] summary + figures written.")
        return

    run_inference(limit=args.limit)
    print("\n[inference OK] results JSONL updated. "
          "Run with --analyze after the full pass.")


if __name__ == "__main__":
    main()
