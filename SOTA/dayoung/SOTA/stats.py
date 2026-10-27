"""질문 단위 bootstrap. A0 Cell 7 / A1 Cell 7 과 동일한 방식이다.

질문을 복원추출한 뒤 그 질문에 속한 행을 전부 모아 평균을 낸다
(= 같은 질문의 C+/C- 가 함께 뽑히거나 함께 빠진다).
행 단위 재표집은 C+/C- 상관을 무시해 CI 를 과소추정한다.

사전등록 판정
  개선      : (방법 - 기준) ΔEM 95% CI 하한 > 0
  C+ 비열등 : (방법 - base)  C+ ΔEM 95% CI 하한 > -2%p   (SAFETY)
"""
from __future__ import annotations

import numpy as np
from scipy.stats import binomtest

SAFETY = -0.02
N_BOOT = 2000


def make_boot(bench, n_boot: int = N_BOOT, seed: int = 0):
    q = bench.m.question.values
    uq = np.unique(q)
    qidx = {u: np.where(q == u)[0] for u in uq}
    rs = np.random.RandomState(seed)
    return [np.concatenate([qidx[u] for u in rs.choice(uq, len(uq))])
            for _ in range(n_boot)]


def ci(v: np.ndarray, boot, mask: np.ndarray | None = None):
    mask = np.ones(len(v), bool) if mask is None else mask
    s = [v[i][mask[i]].mean() for i in boot]
    lo, hi = np.percentile(s, [2.5, 97.5])
    return float(lo), float(hi)


def evaluate(bench, boot, em: np.ndarray, base: np.ndarray,
             ref: np.ndarray | None = None, name: str = "") -> dict:
    """em/base/ref 는 모두 (n_rows,) 0/1 벡터."""
    isCm = bench.is_cneg
    d = em - base
    dr = d if ref is None else em - ref

    lo_p, hi_p = ci(d, boot, ~isCm)
    lo_r, hi_r = ci(dr, boot)

    b01 = int((((ref if ref is not None else base) == 0) & (em == 1)).sum())
    b10 = int((((ref if ref is not None else base) == 1) & (em == 0)).sum())

    out = dict(
        policy=name,
        EM=float(em.mean()),
        dEM=float(d.mean()),
        dC_minus=float(d[isCm].mean()),
        dC_plus=float(d[~isCm].mean()),
        dC_plus_lo=lo_p,
        safe=bool(lo_p > SAFETY),
        vs_ref=float(dr.mean()), vs_ref_lo=lo_r, vs_ref_hi=hi_r,
        improved=bool(lo_r > 0),
        restored=int(((base == 0) & (em == 1)).sum()),
        broken=int(((base == 1) & (em == 0)).sum()),
        mcnemar_p=float(binomtest(b01, b01 + b10).pvalue) if b01 + b10 else 1.0,
    )
    for c in ["K+C+", "K+C-", "K-C+", "K-C-"]:
        msk = bench.cell == c
        out[f"d_{c}"] = float(d[msk].mean()) if msk.any() else float("nan")
    out["pass"] = out["improved"] and out["safe"]
    return out
