#!/usr/bin/env python
"""results/*.json → 보고용 비교표.

  python compare.py --ref base --out table.md

--ref 로 '개선' 판정의 기준을 고른다.
  base          : ①②③를 나란히 올릴 때. 담당 경계가 깨끗하다 (권장)
  always_retain : routing 고유 이득을 따질 때 (A1 보고와 같은 기준)

C+ 비열등은 언제나 base 대비로 판정한다.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from common.artifacts import load_bench
from common.stats import evaluate, make_boot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--ref", default="base")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--out", default="table.md")
    args = ap.parse_args()

    bench = load_bench()
    boot = make_boot(bench, args.n_boot)

    blobs = {}
    for p in sorted(Path(args.results).glob("*.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        blobs[b["method"]] = b

    for need in ("base", args.ref):
        if need not in blobs:
            raise SystemExit(f"{need} 결과가 없다. run.py --method {need} 를 먼저 돌린다.")

    base = np.array(blobs["base"]["em"], dtype=float)
    ref = np.array(blobs[args.ref]["em"], dtype=float)

    rows = []
    for name, b in blobs.items():
        em = np.array(b["em"], dtype=float)
        r = evaluate(bench, boot, em, base,
                     ref=None if name == args.ref else ref, name=name)
        r["family"] = b.get("family", "")
        r["paper"] = b.get("paper", "")
        rows.append(r)

    T = pd.DataFrame(rows).sort_values("EM", ascending=False)
    T.to_csv(Path(args.out).with_suffix(".csv"), index=False)

    mark = lambda x: "O" if x else "X"
    md = [f"| 방법 | 계열 | EM | C+ Δ [하한] | C− Δ | vs {args.ref} Δ [95% CI] "
          "| 개선 | C+ 비열등 | 판정 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for _, r in T.iterrows():
        same = r.policy == args.ref
        md.append(
            f"| {r.policy} | {r.family} | {r.EM*100:.2f} "
            f"| {r.dC_plus*100:+.2f} [{r.dC_plus_lo*100:+.2f}] "
            f"| {r.dC_minus*100:+.2f} "
            f"| {'기준' if same else f'{r.vs_ref*100:+.2f} [{r.vs_ref_lo*100:+.2f}, {r.vs_ref_hi*100:+.2f}]'} "
            f"| {'—' if same else mark(r.improved)} | {mark(r.safe)} "
            f"| {'—' if same else mark(r['pass'])} |")

    md.append(
        f"\n주. 질문 단위 bootstrap {args.n_boot}회(A0/A1 과 동일 방식). "
        f"개선 = vs {args.ref} ΔEM 95% CI 하한 > 0. "
        "C+ 비열등 = C+ ΔEM(vs base) 하한 > −2%p.\n"
        "context-faithful 계열은 변조 답을 gold 로 보는 설계이므로, "
        "사실을 gold 로 채점하는 본 표에서 불리한 것이 정상이다. "
        "성능 열위가 아니라 과제 설정 차이로 해석한다.\n"
        "base 는 A0 산출물(0.5310) 기준이다. packed(E16-2, 0.530)와 한 표로 합칠 때는 "
        "같은 설정으로 base 를 재측정해 단일 기준을 만든다.\n")

    Path(args.out).write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
