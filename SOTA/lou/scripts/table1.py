#!/usr/bin/env python3
"""Helpers for reproducing Lou et al. Table 1 (NQ-Swap) from upstream result JSONs.

Only reads files written by upstream/src/run_resid_projection_ablation.py; it never
runs the model.

  select-ctx-alpha  pick alpha- on the validation grid by Acc_ctx = N_wrong / N
                    (upstream's train_val_test mode only selects by
                    stage2_correct / stage2_runs, i.e. the parametric direction)
  summarize         compute Acc_par / Acc_ctx on the test split for the
                    unsteered, alpha+ and alpha- runs and compare with the paper

Label mapping (upstream/src/plot_nqswap_alpha_curves_multi_model.py):
  stage2_label == "correct"  -> parametric (org_answer substring in first sentence)
  stage2_label == "wrong"    -> contextual (sub_answer present, org_answer absent)
  skipped / not_run          -> counted only in the denominator N (all test rows)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SLUG = "dev__dir_dev__test_dev"
PAPER = {
    "unsteered": {"acc_par": 33.7, "acc_ctx": 49.4},
    "ours": {"acc_par": 56.8, "acc_ctx": 55.5},
}


def _run_dir(root: Path, model: str) -> Path:
    return root / model / "NQ-Swap" / SLUG


def _alpha_tag(a: float) -> str:
    return f"{float(a):g}"


def _load(p: Path) -> dict[str, Any]:
    if not p.is_file():
        sys.exit(f"[table1] not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _val_rates(row: dict[str, Any]) -> tuple[float, float]:
    d = row["summary"]["details"]
    n = max(1, int(d["total_samples"]))
    return int(d["stage2_correct"]) / n, int(d["stage2_wrong"]) / n


def _pick(rows: list[dict[str, Any]], key: int) -> dict[str, Any]:
    """Max rate; ties go to the smaller |alpha| (same rule as upstream _pick_best_alpha)."""
    best = None
    for r in rows:
        s = _val_rates(r)[key]
        if best is None or s > best[0] + 1e-12 or (
            abs(s - best[0]) <= 1e-12 and abs(r["alpha"]) < abs(best[1]["alpha"])
        ):
            best = (s, r)
    assert best is not None
    return best[1]


def cmd_select_ctx_alpha(a: argparse.Namespace) -> None:
    grid = _load(_run_dir(Path(a.sweep_root), a.model) / f"L{a.layer}_val_alpha_grid.json")
    rows = [r for r in grid["alphas_evaluated"] if float(r["alpha"]) < 0]
    if not rows:
        sys.exit("[table1] no negative alphas in the sweep grid")
    best = _pick(rows, key=1)
    par, ctx = _val_rates(best)
    out = {
        "alpha_minus": float(best["alpha"]),
        "selection_metric": "val N_wrong / N (Acc_ctx)",
        "val_acc_par": par,
        "val_acc_ctx": ctx,
        "grid": [
            {"alpha": float(r["alpha"]), "val_acc_par": _val_rates(r)[0], "val_acc_ctx": _val_rates(r)[1]}
            for r in grid["alphas_evaluated"]
        ],
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(_alpha_tag(best["alpha"]))


def _test_metrics(p: Path) -> dict[str, Any]:
    obj = _load(p)
    rows = obj["per_sample_outputs_and_judgements"]["steer_clean_minus_conflict"]
    n = len(rows)
    count = {k: 0 for k in ("correct", "wrong", "skipped", "not_run")}
    for r in rows:
        lab = str(r.get("stage2_label") or "").strip().lower()
        count[lab if lab in count else "skipped"] += 1
    s1 = obj["results"]["stage1_all_samples"]
    return {
        "file": str(p),
        "alpha": float(obj["alpha"]),
        "n_test": n,
        "acc_par": 100.0 * count["correct"] / max(1, n),
        "acc_ctx": 100.0 * count["wrong"] / max(1, n),
        "neither": 100.0 * count["skipped"] / max(1, n),
        "stage1_fail_not_run": 100.0 * count["not_run"] / max(1, n),
        "stage1_rerun_pass_rate": float(s1["rerun_stage1_pass_rate"]),
    }


def cmd_summarize(a: argparse.Namespace) -> None:
    root = Path(a.steer_root)
    L = a.layer
    par_dir = _run_dir(root / "par", a.model)
    par_grid = _load(par_dir / f"L{L}_val_alpha_grid.json")
    a_plus = float(par_grid["best_alpha"])
    a_plus_alt = float(_pick(par_grid["alphas_evaluated"], key=0)["alpha"])
    a_minus = float(_load(root / "ctx" / "selected_alpha.json")["alpha_minus"])

    base = _test_metrics(_run_dir(root / "base", a.model) / f"L{L}_alpha0_steer_result.json")
    par = _test_metrics(par_dir / f"L{L}_alpha{_alpha_tag(a_plus)}_steer_result.json")
    ctx = _test_metrics(_run_dir(root / "ctx", a.model) / f"L{L}_alpha{_alpha_tag(a_minus)}_steer_result.json")

    summary = {
        "model": a.model,
        "layer": L,
        "alpha_plus": a_plus,
        "alpha_plus_selection": "upstream: val stage2_correct / stage2_runs",
        "alpha_plus_if_selected_by_val_acc_par": a_plus_alt,
        "alpha_minus": a_minus,
        "alpha_minus_selection": "scripts/table1.py: val N_wrong / N",
        "unsteered": base,
        "steer_par": par,
        "steer_ctx": ctx,
        "paper": PAPER,
    }
    out = root / "table1_summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"NQ-Swap test, {a.model}, layer {L}, n_test={base['n_test']}")
    print(f"{'':28s}{'Acc_par':>9s}{'Acc_ctx':>9s}{'paper':>16s}")
    print(f"{'Unsteered (alpha=0)':28s}{base['acc_par']:9.1f}{base['acc_ctx']:9.1f}"
          f"{PAPER['unsteered']['acc_par']:8.1f}{PAPER['unsteered']['acc_ctx']:8.1f}")
    print(f"{f'Steer par (alpha={a_plus:g})':28s}{par['acc_par']:9.1f}{'':9s}"
          f"{PAPER['ours']['acc_par']:8.1f}{'':8s}")
    print(f"{f'Steer ctx (alpha={a_minus:g})':28s}{'':9s}{ctx['acc_ctx']:9.1f}"
          f"{'':8s}{PAPER['ours']['acc_ctx']:8.1f}")
    if a_plus_alt != a_plus:
        print(f"[note] val Acc_par/N would select alpha+={a_plus_alt:g} instead of {a_plus:g}")
    print(f"-> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select-ctx-alpha")
    s.add_argument("--sweep-root", required=True)
    s.add_argument("--model", required=True)
    s.add_argument("--layer", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_select_ctx_alpha)
    m = sub.add_parser("summarize")
    m.add_argument("--steer-root", required=True)
    m.add_argument("--model", required=True)
    m.add_argument("--layer", required=True)
    m.set_defaults(fn=cmd_summarize)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
