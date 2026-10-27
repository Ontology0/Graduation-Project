"""산출물 로더.

이 하네스는 기준선을 재구현하지 않는다. A0/A1 에서 이미 검증된 산출물을 읽는다.
  - 현경 공유 폴더 P9/  (읽기 전용) : w_v3, 프롬프트 모듈, 라벨, exp2 대조본
  - 다영 A0_headroom/              : gen_*.parquet (행 단위 raw/pred/em)

재구현하면 A0-4 의 재현 검증(문자열 불일치 <=20/1224)을 다시 통과해야 하는데,
그럴 이유가 없다. 이미 통과한 산출물을 그대로 쓴다.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd

# A0/A1 노트북과 동일한 기본 경로. 환경변수로 덮어쓸 수 있다.
ROOT = os.environ.get("ABENCH_ROOT",
                      "/content/drive/MyDrive/11주차_A축_실험(ldy)/")
P9 = os.environ.get("ABENCH_P9", ROOT + "P9/")
SV3 = P9 + "steer_v3/"
A0 = os.environ.get("ABENCH_A0", ROOT + "A0_headroom/")

# A0-2 와 동일한 md5. 프롬프트 모듈이 바뀌면 기준선 수치가 달라진다.
PROMPT_MD5 = "20959a4c34203ea0866d030baf23595d"

# A0 가 생성한 행동 집합. late_ret_r0.06 이 동결 설정(= always steering).
ARMS = [
    "base",
    "early_ret_r0.03", "early_ret_r0.06", "early_acc_r0.03", "early_acc_r0.06",
    "late_ret_r0.03", "late_ret_r0.06", "late_ret_r0.09", "late_ret_r0.12",
    "late_acc_r0.03", "late_acc_r0.06",
]
REF_ARM = "late_ret_r0.06"


def _md5(path: str, chunk: int = 1 << 24) -> str:
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


@dataclass
class Bench:
    m: pd.DataFrame            # p8s_behavior_v2 (1,224행)
    man: pd.DataFrame          # row_manifest (fold, n_prompt_tok, prompt_md5)
    cb: pd.DataFrame           # cb_v3 (closed-book 답, kside_v3)
    labels: pd.DataFrame       # labels_v3 (ret_x, acc_x, prop)
    PP: object                 # p8s_prompt 모듈
    fold: np.ndarray
    yC: np.ndarray             # 1 = C+
    yK: np.ndarray             # 1 = K+
    cell: np.ndarray           # 'K+C-' 등
    model_revision: str

    @property
    def n(self) -> int:
        return len(self.m)

    @property
    def is_cneg(self) -> np.ndarray:
        return self.yC == 0


def load_bench() -> Bench:
    need = ["hidden_v2/p8s_behavior_v2.csv", "steer_v3/env/row_manifest.parquet",
            "steer_v3/env/manifest_cell1.json", "steer_v3/code/p8s_prompt.py",
            "steer_v3/labels_v3.parquet", "steer_v3/cb_v3.parquet"]
    for f in need:
        if not os.path.exists(P9 + f):
            raise SystemExit(
                f"없음: {P9 + f}\n"
                "P9 공유 폴더 바로가기(읽기 전용)가 연결돼 있는지 먼저 확인한다. "
                "접근이 끊겼다면 현경에게 재공유를 요청해야 한다.")

    sys.path.insert(0, SV3 + "code")
    import p8s_prompt as PP  # noqa: N813
    importlib.reload(PP)
    if _md5(SV3 + "code/p8s_prompt.py") != PROMPT_MD5:
        raise SystemExit("p8s_prompt.py md5 불일치 — 프롬프트가 바뀌면 기준선 수치가 달라진다")

    m = pd.read_csv(P9 + "hidden_v2/p8s_behavior_v2.csv")
    man = pd.read_parquet(SV3 + "env/row_manifest.parquet")
    assert (man.question.values == m.question.values).all(), "row_manifest 정렬 불일치"
    m["rid"] = np.arange(len(m))

    cb = pd.read_parquet(SV3 + "cb_v3.parquet")
    labels = pd.read_parquet(SV3 + "labels_v3.parquet")

    kv = m.question.map(dict(zip(cb.question, cb.kside_v3))).str.replace("−", "-").values
    cl = m.ctx_label.str.replace("−", "-").values
    yK = (kv == "K+").astype(int)
    yC = (cl == "C+").astype(int)

    rev = json.load(open(SV3 + "env/manifest_cell1.json"))["model_revision"]

    return Bench(m=m, man=man, cb=cb, labels=labels, PP=PP,
                 fold=man.fold.values.astype(int), yC=yC, yK=yK,
                 cell=np.array([("K+" if k else "K-") + ("C+" if c else "C-")
                                for k, c in zip(yK, yC)]),
                 model_revision=rev)


def load_arm(name: str) -> pd.DataFrame:
    """A0 가 생성한 행동 결과. rid, raw, pred, em, acc_x, ret_x, hit_limit, rep3, fold."""
    f = A0 + f"gen_{name}.parquet"
    if not os.path.exists(f):
        raise SystemExit(f"없음: {f}\nA0 노트북 A0-4 / A0-5 / A0-5b 를 먼저 실행한다.")
    d = pd.read_parquet(f)
    assert (d.rid.values == np.arange(len(d))).all(), f"{name}: rid 정렬 불일치"
    return d


def load_arm_matrix(arms: list[str] | None = None):
    """(E, preds, names). E=(n_rows, n_arms) 0/1, preds=(n_rows, n_arms) 문자열."""
    arms = arms or ARMS
    ds = [load_arm(a) for a in arms]
    E = np.stack([d.em.values.astype(float) for d in ds], 1)
    P = np.stack([d.pred.values.astype(object) for d in ds], 1)
    ref = E[:, arms.index(REF_ARM)].mean()
    if abs(ref - 0.5997) > 1e-3:
        print(f"[경고] {REF_ARM} EM {ref:.4f} — A0 보고값 0.5997 과 다르다")
    return E, P, arms
