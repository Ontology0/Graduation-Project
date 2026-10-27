"""기준선 ② always steering (및 base, 기타 arm) — A0 산출물 조회.

재구현하지 않는다. A0-4 에서 현경 exp2_P9_r0.06 대비 문자열 불일치 <=20/1224 로
검증을 통과한 산출물을 그대로 읽는다.

  base              gen_base.parquet              EM 0.5310
  always_retain     gen_late_ret_r0.06.parquet    EM 0.5997  (P9, rho0.06, L14-18, w_v3)
  always_retain_r09 gen_late_ret_r0.09.parquet    EM 0.6005  (C+ 비열등 실패 사례)

GPU 불필요.
"""
from __future__ import annotations

import numpy as np

from common.artifacts import load_arm
from common.scoring import stability

from .base import LookupMethod, register


class _Arm(LookupMethod):
    arm = "base"
    family = "ours"

    def run(self):
        d = load_arm(self.arm)
        st = stability(d)
        if not st["stable"]:
            print(f"[경고] {self.arm} 불안정 "
                  f"(hit_limit {st['hit_limit']:.3f}, rep3 {st['rep3']:.3f})")
        return d.em.values.astype(float), list(d.pred.values)


@register("base")
class Base(_Arm):
    arm = "base"
    paper = "내부 (A0 gen_base)"


@register("always_retain")
class AlwaysRetain(_Arm):
    arm = "late_ret_r0.06"
    paper = "내부 (현경 Steering_develop Exp2 동결 설정 / A0 재현)"
    expected_em = 0.5997


@register("always_retain_r09")
class AlwaysRetainStrong(_Arm):
    """rho0.09. C- 는 +16.67%p 로 더 오르지만 C+ 하한 -5.07%p 로 비열등 실패.
    '강도를 올리려면 routing 이 필요하다'는 주장의 대조군."""
    arm = "late_ret_r0.09"
    paper = "내부 (A1 3-2)"
    expected_em = 0.6005


@register("always_early_retain")
class AlwaysEarlyRetain(_Arm):
    arm = "early_ret_r0.06"
    paper = "내부 (A0)"


def check_expected(name: str, em: np.ndarray, tol: float = 5e-3) -> None:
    from .base import REGISTRY
    exp = getattr(REGISTRY.get(name), "expected_em", None)
    if exp is None:
        return
    got = float(em.mean())
    flag = "OK" if abs(got - exp) <= tol else "불일치"
    print(f"[재현 확인] {name}: EM {got:.4f} vs 보고값 {exp:.4f}  → {flag}")
