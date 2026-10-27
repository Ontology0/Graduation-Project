"""기준선 ① routing — A1 late-only (이득 예측) router.

A1 Cell 2~4 의 로직을 그대로 옮겼다. GPU 불필요:
한 행에는 early/late 중 하나만 개입하므로 greedy 에서는 결과표 조회가 실제 생성과 같다.
따라서 router 의 예측 = 선택된 arm 의 저장된 pred 문자열이다.

보고값: EM 0.6078, Always-retain 대비 +0.82%p [-0.49, +2.21], C- +14.54, C+ +0.82
"""
from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler

from common.artifacts import ARMS, P9, REF_ARM, load_arm_matrix

from .base import LookupMethod, register

SEED, PCA_DIM = 0, 128
L_EARLY, L_LATE = 7, 13          # 판독층 (0-based). 개입은 L8-12 / L14-18
SEL_CP_MIN = -0.01               # 선택 단계 inner C+ ΔEM 하한

GRID_MARGIN = [-9, 0.0, 0.02, 0.05, 0.1]


@register("late_router")
class LateOnlyGainRouter(LookupMethod):
    paper = "내부 (A1 late-only 이득 router)"
    family = "ours"
    expected_em = 0.6078

    def __init__(self, bench, policy: str = "late_gain"):
        super().__init__(bench)
        self.policy = policy          # 'late_gain' | 'early_gain' | 'staged_gain'

    # ------------------------------------------------------------ 판독 모델

    def _load(self):
        b = self.bench
        E, P, names = load_arm_matrix(ARMS)
        self.E, self.P, self.names = E, P, names
        self.base = E[:, names.index("base")]
        self.G = E - self.base[:, None]
        self.iE = np.array([i for i, n in enumerate(names) if n.startswith("early")])
        self.iL = np.array([i for i, n in enumerate(names) if n.startswith("late")])

        H = np.load(P9 + "hidden_v2/p8s_v2_h_out.npy", mmap_mode="r")
        self.X = {"7": np.asarray(H[:, L_EARLY]).astype(np.float32),
                  "13": np.asarray(H[:, L_LATE]).astype(np.float32)}
        self.q = b.m.question.values

    def _fit_predict(self, tr, te) -> dict:
        """A1 Cell 3 fit_predict 와 동일."""
        out = {}
        for tag in ("7", "13"):
            X = self.X[tag]
            sc = StandardScaler().fit(X[tr])
            pca = PCA(PCA_DIM, random_state=SEED).fit(sc.transform(X[tr]))
            Ztr = pca.transform(sc.transform(X[tr]))
            Zte = pca.transform(sc.transform(X[te]))
            zs = StandardScaler().fit(Ztr)
            Ztr, Zte = zs.transform(Ztr), zs.transform(Zte)

            out["pK" + tag] = LogisticRegression(C=0.1, max_iter=3000) \
                .fit(Ztr, self.bench.yK[tr]).predict_proba(Zte)[:, 1]
            if tag == "13":
                out["pC13"] = LogisticRegression(C=0.1, max_iter=3000) \
                    .fit(Ztr, self.bench.yC[tr]).predict_proba(Zte)[:, 1]
            idx = self.iE if tag == "7" else self.iL
            out["g" + tag] = Ridge(alpha=100.0).fit(Ztr, self.G[tr][:, idx]).predict(Zte)
        return out

    def _oof(self, rows, n_split: int = 4, seed: int = SEED) -> dict:
        uq = np.unique(self.q[rows])
        rng = np.random.RandomState(seed)
        rng.shuffle(uq)
        grp = {u: i % n_split for i, u in enumerate(uq)}
        g = np.array([grp[x] for x in self.q[rows]])
        out = None
        for j in range(n_split):
            Pj = self._fit_predict(rows[g != j], rows[g == j])
            if out is None:
                out = {k: np.zeros((len(rows),) + v.shape[1:]) for k, v in Pj.items()}
            for k, v in Pj.items():
                out[k][g == j] = v
        return out

    # ------------------------------------------------------------ 정책

    def _pol_gain(self, P, key, idxs, margin):
        g = P[key]
        a = idxs[g.argmax(1)].copy()
        a[g.max(1) < margin] = 0          # 0 = base = no-op
        return a

    def _apply(self, P, prm):
        if self.policy == "early_gain":
            return self._pol_gain(P, "g7", self.iE, prm["margin"])
        if self.policy == "late_gain":
            return self._pol_gain(P, "g13", self.iL, prm["margin"])
        if self.policy == "staged_gain":
            e = self._pol_gain(P, "g7", self.iE, prm["te"])
            l = self._pol_gain(P, "g13", self.iL, prm["margin"])
            return np.where(e > 0, e, l)
        raise ValueError(self.policy)

    def _fit_policy(self, P_in, rows):
        """nested 선택. inner C+ ΔEM >= SEL_CP_MIN 후보 우선, 그 안에서 EM 최대."""
        grid = ([dict(margin=mg) for mg in GRID_MARGIN] if self.policy != "staged_gain"
                else [dict(te=te, margin=mg) for te in [0.02, 0.05, 0.1, 0.2, 9]
                      for mg in [-9, 0.0, 0.05]])
        best = None
        isCm = self.bench.is_cneg
        for prm in grid:
            a = self._apply(P_in, prm)
            em = self.E[rows, a].mean()
            cp = (self.E[rows, a] - self.base[rows])[~isCm[rows]].mean()
            key = (cp >= SEL_CP_MIN, em)
            if best is None or key > best[0]:
                best = (key, prm)
        return best[1]

    # ------------------------------------------------------------ 실행

    def run(self):
        self._load()
        fold = self.bench.fold
        choice = np.zeros(self.bench.n, int)
        picked = []

        for k in range(5):
            tr = np.where(fold != k)[0]
            te = np.where(fold == k)[0]
            P_in = self._oof(tr, seed=SEED + k)     # 선택용 (test 미사용)
            P_te = self._fit_predict(tr, te)        # 적용용
            prm = self._fit_policy(P_in, tr)
            choice[te] = self._apply(P_te, prm)
            picked.append({"fold": k, **prm})

        self.selected = picked
        self.action_dist = {self.names[a]: float((choice == a).mean())
                            for a in np.unique(choice)}
        print("[router] fold별 선택:", picked)
        print("[router] 행동 분포:",
              {k: round(v, 3) for k, v in sorted(self.action_dist.items(),
                                                 key=lambda x: -x[1])})

        rows = np.arange(self.bench.n)
        em = self.E[rows, choice]
        preds = [self.P[i, choice[i]] for i in rows]
        return em.astype(float), preds


@register("ref_always_for_router")
class _Ref(LookupMethod):
    """router 비교 기준(Always-retain)을 같은 조회 경로로 꺼내기 위한 보조."""
    family = "ours"

    def run(self):
        E, P, names = load_arm_matrix(ARMS)
        j = names.index(REF_ARM)
        return E[:, j].astype(float), list(P[:, j])
