"""채점. A0 노트북 Cell 6/10 의 trunc_v3 / score_v3 와 동일하다.

정규화는 반드시 PP.norm(p8s_prompt) 을 쓴다. SQuAD 표준 정규화로 바꾸면
A0/A1 보고값과 어긋나 비교가 깨진다. 이 파일은 고치지 않는다.
"""
from __future__ import annotations

import json
import re
from collections import Counter

import numpy as np
import pandas as pd

_ABBR = r"(?<!\bDr)(?<!\bMr)(?<!\bMs)(?<!\bMrs)(?<!\bSt)(?<!\bJr)(?<!\bSr)(?<!\b[A-Z])"


def trunc_v3(raw) -> str:
    s = str(raw).strip().split("\n")[0].strip()
    s = re.sub(r"^(answer|the answer is)\s*:?\s*", "", s, flags=re.I)
    if len(s.split()) > 8:
        s = re.split(_ABBR + r"\.\s+(?=[A-Z])", s)[0]
    return re.sub(r"[.,;:\s]+$", "", s.strip().strip("\"'")).strip()


def rep3(t) -> int:
    w = str(t).split()
    g = Counter(tuple(w[i:i + 3]) for i in range(len(w) - 2))
    return int(bool(g) and max(g.values()) >= 3)


def make_scorer(bench):
    """score(df) -> df. df 는 rid, raw, n_tok 를 가진다."""
    PP = bench.PP
    m, cb = bench.m, bench.cb
    gl_row = [json.loads(g) if isinstance(g, str) else list(g) for g in m.gold]
    cbq = dict(zip(cb.question, cb.cb_greedy_v3))
    surf = m.answer_surface.map(PP.norm).values
    cbn = m.question.map(cbq).map(PP.norm).values

    def score(d: pd.DataFrame) -> pd.DataFrame:
        p = [PP.norm(trunc_v3(x)) for x in d.raw]
        d["pred"] = [trunc_v3(x) for x in d.raw]
        d["em"] = [int(any(pi == PP.norm(g) for g in gg))
                   for pi, gg in zip(p, gl_row)]
        d["acc_x"] = [int(s != "" and pi == s) for pi, s in zip(p, surf)]
        d["ret_x"] = [int(c != "" and c != s and pi == c)
                      for pi, s, c in zip(p, surf, cbn)]
        d["hit_limit"] = (d.n_tok >= PP.MAX_NEW_TOKENS).astype(int)
        d["rep3"] = d.raw.map(rep3)
        return d

    return score


def em_from_preds(bench, preds: list[str]) -> np.ndarray:
    """이미 잘린 pred 문자열 목록 → 0/1 EM 벡터."""
    PP = bench.PP
    gl_row = [json.loads(g) if isinstance(g, str) else list(g) for g in bench.m.gold]
    return np.array([int(any(PP.norm(p) == PP.norm(g) for g in gg))
                     for p, gg in zip(preds, gl_row)], dtype=float)


def stability(d: pd.DataFrame) -> dict:
    """A0 의 arm 안정성 기준. 둘 다 0.05 이하여야 신뢰한다."""
    return {"hit_limit": float(d.hit_limit.mean()), "rep3": float(d.rep3.mean()),
            "stable": bool(d.hit_limit.mean() <= .05 and d.rep3.mean() <= .05)}
