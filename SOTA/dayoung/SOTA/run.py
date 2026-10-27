#!/usr/bin/env python
"""메서드 하나 실행 → results/<name>.json

  # 기준선 (CPU, 즉시)
  python run.py --method base
  python run.py --method always_retain
  python run.py --method late_router

  # SOTA (GPU)
  python run.py --method cad
  python run.py --method spare

경로는 환경변수로 바꾼다:
  ABENCH_ROOT / ABENCH_P9 / ABENCH_A0
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np


def load_registry():
    # 기준선은 torch 없이 돌아간다. SOTA 모듈은 torch 가 있을 때만 등록한다.
    from methods import base, ours_lookup, ours_router  # noqa: F401
    try:
        from methods import sota_contrastive, sota_stubs  # noqa: F401
    except ImportError as e:
        print(f"[알림] SOTA 모듈 미등록 ({e}). 기준선만 실행할 수 있다.")
    from methods.base import REGISTRY
    return REGISTRY


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", required=True)
    ap.add_argument("--out", default="results")
    ap.add_argument("--no-version-check", action="store_true",
                    help="transformers 5.17.0 확인을 건너뛴다 (권장하지 않음)")
    args = ap.parse_args()

    REGISTRY = load_registry()
    if args.method not in REGISTRY:
        raise SystemExit(f"미등록: {args.method}\n가능: {sorted(REGISTRY)}")
    cls = REGISTRY[args.method]

    if cls.needs_gpu:
        from common.generate import setup_determinism
        setup_determinism()          # CUDA 초기화 전

    from common.artifacts import load_bench
    bench = load_bench()
    print(f"[bench] {bench.n}행 / 셀 분포 "
          f"{dict(zip(*np.unique(bench.cell, return_counts=True)))}")

    t0 = time.time()
    if cls.needs_gpu:
        from common.generate import Runner
        method = cls(bench, Runner(bench, check_version=not args.no_version_check))
    else:
        method = cls(bench)

    em, preds = method.run()
    elapsed = time.time() - t0

    from methods.ours_lookup import check_expected
    check_expected(args.method, em)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "method": args.method,
        "paper": cls.paper,
        "family": cls.family,
        "needs_gpu": cls.needs_gpu,
        "model_revision": bench.model_revision,
        "em_all": float(em.mean()),
        "em_cpos": float(em[~bench.is_cneg].mean()),
        "em_cneg": float(em[bench.is_cneg].mean()),
        "em": [int(x) for x in em],
        "pred": list(preds),
        "sec_total": round(elapsed, 1),
    }
    if hasattr(method, "selected"):
        payload["selected_params"] = method.selected
        payload["action_dist"] = method.action_dist

    (out / f"{args.method}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n[{args.method}] EM {em.mean():.4f} "
          f"| C+ {em[~bench.is_cneg].mean():.4f} | C- {em[bench.is_cneg].mean():.4f} "
          f"({elapsed/60:.1f}분)")
    print(f"→ {out / (args.method + '.json')}")


if __name__ == "__main__":
    main()
