#!/usr/bin/env python3
"""Re-score upstream NQ-Swap test outputs with the paper's Appendix C protocol.

Reads the unsteered / alpha+ / alpha- test files (L<layer>_alpha<a>_steer_result.json)
written by upstream/src/run_resid_projection_ablation.py. No model is run and no alpha
is re-selected; the alphas are whatever table1.py / upstream already chose.

Paper protocol (Appendix C):
  C.1 normalize answers and output: lowercase; remove punctuation except intra-token
      hyphens; remove leading articles (a, an, the); collapse whitespace
  C.2 match within the first 256 generated tokens. Upstream generates at most 200
      tokens (max_new_tokens=200), so the whole stage2_output_raw is used, not cut at
      the first sentence as upstream does
  C.3 four exclusive labels: par-only, ctx-only, both, neither
      Acc_par = par-only / N, Acc_ctx = ctx-only / N
N = all test rows (same as upstream). Rows whose stage2 was not run (steered stage1
failed, upstream "not_run") count as neither.

Answer lists: org_answer = parametric aliases, sub_answer = contextual aliases. Upstream
per-row test outputs keep only the first sub_answer (distracted_token), so full lists are
taken from the dump manifest by line_idx.

Results are added to <steer-root>/table1_summary.json under "paper_metric".
"""
from __future__ import annotations

import argparse
import json
import re
import string
import sys
from pathlib import Path
from typing import Any

LABELS = ("par_only", "ctx_only", "both", "neither")
SHORT_MAX_LEN = 3  # aux: normalized answers this short are prone to accidental substring hits
RUNS = (("unsteered", "unsteered"), ("steer_par", "steer_par"), ("steer_ctx", "steer_ctx"))

_PUNCT_NO_HYPHEN = re.escape("".join(c for c in string.punctuation if c != "-"))
_PUNCT_RE = re.compile(f"[{_PUNCT_NO_HYPHEN}‘’“”–—…]")
# Hyphens survive only between two alphanumerics ("x-ray"); others are removed.
_LONE_HYPHEN_RE = re.compile(r"(?<![0-9A-Za-z])-|-(?![0-9A-Za-z])")
_LEADING_ARTICLE_RE = re.compile(r"^(?:a|an|the)\s+")


def normalize(s: Any) -> str:
    t = str(s or "").lower()
    t = _PUNCT_RE.sub("", t)
    t = _LONE_HYPHEN_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = _LEADING_ARTICLE_RE.sub("", t)
    return t


def _contains(s: str, answers: list[str], word_boundary: bool) -> bool:
    for a in (normalize(x) for x in answers):
        if not a:
            continue
        if word_boundary:
            if re.search(rf"\b{re.escape(a)}\b", s):
                return True
        elif a in s:
            return True
    return False


def label_row(
    output: str | None, par_answers: list[str], ctx_answers: list[str], *, word_boundary: bool = False
) -> str:
    """Paper metric uses word_boundary=False (plain substring, Appendix C.3)."""
    if not output:
        return "neither"
    s = normalize(output)
    if not s:
        return "neither"
    has_par = _contains(s, par_answers, word_boundary)
    has_ctx = _contains(s, ctx_answers, word_boundary)
    if has_par and has_ctx:
        return "both"
    if has_par:
        return "par_only"
    if has_ctx:
        return "ctx_only"
    return "neither"


def _answers_by_line(manifest: Path) -> dict[int, tuple[list[str], list[str]]]:
    obj = json.loads(manifest.read_text(encoding="utf-8"))
    out: dict[int, tuple[list[str], list[str]]] = {}
    for s in obj.get("samples", []):
        li = int(s["line_idx"])
        if li in out:
            sys.exit(f"[rescore] duplicate line_idx {li} in {manifest}")
        out[li] = (
            [str(x) for x in s.get("gold_answers", [])],
            [str(x) for x in (s.get("distracted_tokens") or [s.get("distracted_token", "")])],
        )
    return out


def rescore(test_file: Path, answers: dict[int, tuple[list[str], list[str]]]) -> dict[str, Any]:
    obj = json.loads(test_file.read_text(encoding="utf-8"))
    rows = obj["per_sample_outputs_and_judgements"]["steer_clean_minus_conflict"]
    n = len(rows)
    counts = {k: 0 for k in LABELS}
    wb_counts = {k: 0 for k in LABELS}
    short = {"any": 0, "par": 0, "ctx": 0}
    upstream_counts = {"correct": 0, "wrong": 0, "skipped": 0, "not_run": 0}
    for r in rows:
        li = int(r["line_idx"])
        if li not in answers:
            sys.exit(f"[rescore] line_idx {li} from {test_file} not in manifest")
        par_a, ctx_a = answers[li]
        up = str(r.get("stage2_label") or "").strip().lower()
        upstream_counts[up if up in upstream_counts else "skipped"] += 1
        out = r.get("stage2_output_raw") if r.get("stage2_evaluated") else None
        counts[label_row(out, par_a, ctx_a)] += 1
        wb_counts[label_row(out, par_a, ctx_a, word_boundary=True)] += 1
        sp = any(0 < len(normalize(x)) <= SHORT_MAX_LEN for x in par_a)
        sc = any(0 < len(normalize(x)) <= SHORT_MAX_LEN for x in ctx_a)
        short["par"] += sp
        short["ctx"] += sc
        short["any"] += sp or sc
    pct = lambda c: 100.0 * c / max(1, n)  # noqa: E731
    return {
        "file": str(test_file),
        "alpha": float(obj["alpha"]),
        "n_test": n,
        "upstream": {
            "acc_par": pct(upstream_counts["correct"]),
            "acc_ctx": pct(upstream_counts["wrong"]),
            "counts": upstream_counts,
        },
        "paper": {
            "acc_par": pct(counts["par_only"]),
            "acc_ctx": pct(counts["ctx_only"]),
            "counts": counts,
            "dist_pct": {k: pct(v) for k, v in counts.items()},
        },
        # Auxiliary diagnostics only; not the reported metric.
        "aux": {
            "short_answer_max_len": SHORT_MAX_LEN,
            "rows_with_short_answer": short,
            "word_boundary": {
                "acc_par": pct(wb_counts["par_only"]),
                "acc_ctx": pct(wb_counts["ctx_only"]),
                "counts": wb_counts,
                "dist_pct": {k: pct(v) for k, v in wb_counts.items()},
            },
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--steer-root", required=True, help="dir holding table1_summary.json")
    ap.add_argument("--manifest", required=True,
                    help="dump internal_aware_data__stage1_correct_use_wrong_context.json")
    ap.add_argument("--base", help="unsteered test file (default: from table1_summary.json)")
    ap.add_argument("--par", help="alpha+ test file (default: from table1_summary.json)")
    ap.add_argument("--ctx", help="alpha- test file (default: from table1_summary.json)")
    a = ap.parse_args()

    summary_path = Path(a.steer_root) / "table1_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    override = {"unsteered": a.base, "steer_par": a.par, "steer_ctx": a.ctx}
    answers = _answers_by_line(Path(a.manifest))

    res: dict[str, Any] = {}
    for key, skey in RUNS:
        f = override[key] or (summary.get(skey) or {}).get("file")
        if not f:
            flag = {"unsteered": "--base", "steer_par": "--par", "steer_ctx": "--ctx"}[key]
            sys.exit(f"[rescore] no test file for {key}: pass {flag} or run table1.py summarize first")
        res[key] = rescore(Path(f), answers)

    paper_ref = summary.get("paper") or {
        "unsteered": {"acc_par": 33.7, "acc_ctx": 49.4},
        "ours": {"acc_par": 56.8, "acc_ctx": 55.5},
    }
    print(f"\nNQ-Swap test re-score (n_test={res['unsteered']['n_test']}); "
          "upstream = first sentence, 'correct' includes both | paper = full output (<=200 tok), App. C")
    hdr = f"{'run':24s}{'up par':>8s}{'up ctx':>8s}{'pp par':>8s}{'pp ctx':>8s}" \
          f"{'par-only':>10s}{'ctx-only':>10s}{'both':>7s}{'neither':>9s}{'Table1':>14s}"
    print(hdr)
    ref = {"unsteered": paper_ref["unsteered"], "steer_par": paper_ref["ours"], "steer_ctx": paper_ref["ours"]}
    for key, _ in RUNS:
        r = res[key]
        d = r["paper"]["dist_pct"]
        name = f"{key} (a={r['alpha']:g})"
        tgt = ref[key]
        tgt_s = (f"{tgt['acc_par']:.1f}/{tgt['acc_ctx']:.1f}" if key == "unsteered"
                 else f"par {tgt['acc_par']:.1f}" if key == "steer_par" else f"ctx {tgt['acc_ctx']:.1f}")
        print(f"{name:24s}{r['upstream']['acc_par']:8.1f}{r['upstream']['acc_ctx']:8.1f}"
              f"{r['paper']['acc_par']:8.1f}{r['paper']['acc_ctx']:8.1f}"
              f"{d['par_only']:10.1f}{d['ctx_only']:10.1f}{d['both']:7.1f}{d['neither']:9.1f}{tgt_s:>14s}")

    print(f"\n[aux, not the reported metric] word-boundary match (\\b) on the same normalized text; "
          f"rows with a normalized answer of <= {SHORT_MAX_LEN} chars")
    print(f"{'run':24s}{'wb par':>8s}{'wb ctx':>8s}{'par-only':>10s}{'ctx-only':>10s}{'both':>7s}{'neither':>9s}"
          f"{'short any':>11s}{'par':>6s}{'ctx':>6s}")
    for key, _ in RUNS:
        r = res[key]
        wb = r["aux"]["word_boundary"]
        d = wb["dist_pct"]
        sh = r["aux"]["rows_with_short_answer"]
        name = f"{key} (a={r['alpha']:g})"
        print(f"{name:24s}{wb['acc_par']:8.1f}{wb['acc_ctx']:8.1f}"
              f"{d['par_only']:10.1f}{d['ctx_only']:10.1f}{d['both']:7.1f}{d['neither']:9.1f}"
              f"{sh['any']:11d}{sh['par']:6d}{sh['ctx']:6d}")

    summary["paper_metric"] = {
        "protocol": "Appendix C: lowercase, strip punctuation except intra-token hyphens, drop leading "
                    "article, collapse whitespace; substring match on full stage2_output_raw "
                    "(max_new_tokens=200 < paper's 256-token window); not_run -> neither; N = all test rows",
        "manifest": str(a.manifest),
        "runs": res,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"-> {summary_path} (paper_metric)")


if __name__ == "__main__":
    main()
