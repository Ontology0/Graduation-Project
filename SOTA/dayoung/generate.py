"""생성 파이프라인. A0 노트북 A0-3 과 동일하게 맞춘다.

SOTA 를 새로 생성할 때만 쓴다. 기준선 ①②는 산출물 조회라 이 파일이 필요 없다.

A0 와 반드시 같아야 하는 것 (하나라도 다르면 기준선과 비교 불가)
  - transformers==5.17.0, model revision 고정, deterministic, tf32 off
  - PP.build_messages + apply_chat_template, 행별 prompt_md5 검증
  - padding_side='left', BS=16, n_prompt_tok 정렬
  - EOS 에 <|eot_id|> 포함, max_new_tokens = PP.MAX_NEW_TOKENS
  - steering: prefill 은 attention mask 로 비패딩 토큰 전체(P9), decode 는 마지막 위치
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import pandas as pd
import torch

BS = 16


def setup_determinism() -> None:
    """CUDA 초기화 전에 호출한다. A0-1 과 동일."""
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False


class Runner:
    def __init__(self, bench, check_version: bool = True):
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if check_version and transformers.__version__ != "5.17.0":
            raise SystemExit(
                f"transformers {transformers.__version__} — A0 는 5.17.0 에서 측정했다. "
                "버전이 다르면 기준선과 비교할 수 없다. "
                "의도적으로 넘기려면 check_version=False.")

        self.bench = bench
        PP = bench.PP
        self.PP = PP

        self.tok = AutoTokenizer.from_pretrained(PP.MODEL_ID,
                                                 revision=bench.model_revision)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            PP.MODEL_ID, revision=bench.model_revision, dtype=torch.bfloat16,
            device_map="auto", attn_implementation="sdpa").eval()

        self.eos_ids = sorted({self.tok.eos_token_id,
                               self.tok.convert_tokens_to_ids("<|eot_id|>")} - {None})
        self.decode_kw = dict(skip_special_tokens=True,
                              clean_up_tokenization_spaces=False)

        m, man = bench.m, bench.man
        prompts = [self.tok.apply_chat_template(
            PP.build_messages(r.question, r.ctx_text),
            tokenize=False, add_generation_prompt=True) for r in m.itertuples()]
        bad = sum(hashlib.md5(p.encode()).hexdigest() != h
                  for p, h in zip(prompts, man.prompt_md5))
        if bad:
            raise SystemExit(f"프롬프트 해시 불일치 {bad}행 — A0 와 다른 프롬프트다")
        self.prompts = np.array(prompts, dtype=object)

        self.fold_rows = {
            k: m[man.fold.values == k]
                 .assign(n_prompt_tok=man.n_prompt_tok.values[man.fold.values == k])
                 .sort_values(["n_prompt_tok", "rid"], kind="stable").rid.values
            for k in range(5)}

        self.steer = _Steer(self.model)

    # ------------------------------------------------------------ 생성

    @torch.no_grad()
    def generate_rows(self, rids: np.ndarray) -> dict[int, tuple[str, int]]:
        out = {}
        for s in range(0, len(rids), BS):
            b = rids[s:s + BS]
            enc = self.tok(self.prompts[b].tolist(), return_tensors="pt",
                           padding=True, add_special_tokens=False).to(self.model.device)
            self.steer.mask = enc.attention_mask.clone()
            g = self.model.generate(**enc, max_new_tokens=self.PP.MAX_NEW_TOKENS,
                                    do_sample=False, pad_token_id=self.tok.pad_token_id,
                                    eos_token_id=self.eos_ids)[:, enc.input_ids.shape[1]:]
            for r, row in zip(b, g.tolist()):
                stop = next((i for i, t in enumerate(row) if t in self.eos_ids), None)
                n = stop if stop is not None else len(row)
                out[int(r)] = (self.tok.decode(row[:n], **self.decode_kw), n)
        return out

    def run_all(self) -> pd.DataFrame:
        """fold 순서대로 전 행 생성 → rid 정렬 DataFrame(raw, n_tok, fold)."""
        rows = []
        for k in range(5):
            o = self.generate_rows(self.fold_rows[k])
            rows += [dict(rid=r, raw=x, n_tok=n, fold=k) for r, (x, n) in o.items()]
        return pd.DataFrame(rows).sort_values("rid").reset_index(drop=True)


class _Steer:
    """A0 의 SteerA 와 같은 연산."""

    def __init__(self, model, layers=range(8, 19)):
        self.model = model
        self.layers = list(layers)
        self.vec, self.scale, self.mask, self.calls = None, {}, None, {}
        self.h = [model.model.layers[L].register_forward_hook(self._mk(L))
                  for L in self.layers]

    def _mk(self, L):
        def hook(mod, args, out):
            if self.vec is None or L not in self.vec:
                return out
            h = out[0] if isinstance(out, (tuple, list)) else out
            d = (self.scale[L] * self.vec[L]).to(h.dtype)
            self.calls[L] = self.calls.get(L, 0) + 1
            if h.shape[1] > 1:
                h += self.mask[:, :, None].to(h.dtype) * d      # prefill (P9)
            else:
                h[:, -1, :] += d                                 # decode
            return out
        return hook

    def set(self, vec=None, scale=None):
        self.vec = None if vec is None else {
            L: torch.as_tensor(v, device=self.model.device, dtype=self.model.dtype)
            for L, v in vec.items()}
        self.scale, self.calls = (scale or {}), {}

    def remove(self):
        for x in self.h:
            x.remove()
