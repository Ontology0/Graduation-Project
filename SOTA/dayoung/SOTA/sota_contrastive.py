"""로짓 산술 계열 SOTA (CAD / AdaCAD).

이 계열은 context-faithful 가족이다. 원논문은 변조된 문맥의 답을 gold 로 보지만,
본 하네스는 p8s 의 gold(사실)로 채점한다. 따라서 C- 에서 base 보다 낮게 나오는 것이
정상이며, 그 자체가 '과제 설정이 다르다'는 증거다. 이기기 위한 비교가 아니다.

  CAD    (Shi et al., 2023)  : logit = (1+a)*logit_ctx - a*logit_cb,  a=1.0
  AdaCAD (Wang et al., 2024) : a 를 JSD(p_ctx || p_cb) 로 행마다 적응 조절

둘 다 CB 패스를 따로 돌리므로 2-pass 다. 비용 비교 축에 그대로 쓸 수 있다.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from common.scoring import make_scorer

from .base import GenMethod, register


def _jsd(p: torch.Tensor, q: torch.Tensor) -> float:
    m = 0.5 * (p + q)
    kl = lambda a, b: (a * (a.clamp_min(1e-12).log() - b.clamp_min(1e-12).log())).sum()
    return float(0.5 * kl(p, m) + 0.5 * kl(q, m))


class _Contrastive(GenMethod):
    adaptive = False
    alpha = 1.0
    family = "context-faithful"

    @torch.no_grad()
    def _one(self, rid: int) -> tuple[str, int]:
        r = self.runner
        tok, model, PP = r.tok, r.model, r.PP
        row = self.bench.m.iloc[rid]

        p_ctx = r.prompts[rid]
        p_cb = tok.apply_chat_template(PP.build_messages(row.question, None),
                                       tokenize=False, add_generation_prompt=True)

        ids_ctx = tok(p_ctx, return_tensors="pt", add_special_tokens=False).to(model.device)
        ids_cb = tok(p_cb, return_tensors="pt", add_special_tokens=False).to(model.device)

        cur_ctx, cur_cb = ids_ctx.input_ids, ids_cb.input_ids
        past_ctx = past_cb = None
        out_ids: list[int] = []

        for _ in range(PP.MAX_NEW_TOKENS):
            o_ctx = model(input_ids=cur_ctx, past_key_values=past_ctx, use_cache=True)
            o_cb = model(input_ids=cur_cb, past_key_values=past_cb, use_cache=True)
            past_ctx, past_cb = o_ctx.past_key_values, o_cb.past_key_values

            l_ctx = o_ctx.logits[0, -1].float()
            l_cb = o_cb.logits[0, -1].float()
            a = _jsd(F.softmax(l_ctx, -1), F.softmax(l_cb, -1)) if self.adaptive else self.alpha

            nxt = int(((1 + a) * l_ctx - a * l_cb).argmax())
            if nxt in r.eos_ids:
                break
            out_ids.append(nxt)
            t = torch.tensor([[nxt]], device=model.device)
            cur_ctx = cur_cb = t

        return tok.decode(out_ids, **r.decode_kw), len(out_ids)

    def run(self):
        rows = []
        for rid in range(self.bench.n):
            raw, n = self._one(rid)
            rows.append(dict(rid=rid, raw=raw, n_tok=n,
                             fold=int(self.bench.fold[rid])))
            if (rid + 1) % 100 == 0:
                print(f"  {rid+1}/{self.bench.n}")
        d = make_scorer(self.bench)(pd.DataFrame(rows))
        return d.em.values.astype(float), list(d.pred.values)


@register("cad")
class CAD(_Contrastive):
    paper = "Trusting Your Evidence (Shi et al., arXiv 2305.14739)"
    adaptive = False

    def __init__(self, bench, runner, alpha: float = 1.0):
        super().__init__(bench, runner)
        self.alpha = alpha


@register("adacad")
class AdaCAD(_Contrastive):
    paper = "AdaCAD (Wang et al., 2024)"
    adaptive = True
