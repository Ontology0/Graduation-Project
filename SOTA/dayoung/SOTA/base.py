"""메서드 인터페이스.

두 종류가 있다.
  LookupMethod : A0 산출물을 조회한다. GPU 불필요. 기준선 ①②가 여기 속한다.
  GenMethod    : 새로 생성한다. GPU 필요. SOTA 가 여기 속한다.

팀원이 논문을 맡으면 GenMethod 하나를 상속해 methods/ 에 추가한다.
common/ 은 고치지 않는다. 고치는 순간 서로 비교가 불가능해진다.
"""
from __future__ import annotations

import numpy as np

REGISTRY: dict[str, type] = {}


def register(name: str):
    def deco(cls):
        REGISTRY[name] = cls
        cls.name = name
        return cls
    return deco


class Method:
    name = "unnamed"
    paper = ""
    #: 'ours' | 'conflict-resolution' | 'context-faithful'
    family = ""
    needs_gpu = False

    def __init__(self, bench):
        self.bench = bench

    def run(self) -> tuple[np.ndarray, list[str]]:
        """(em 벡터 (n_rows,), pred 문자열 목록) 반환."""
        raise NotImplementedError


class LookupMethod(Method):
    needs_gpu = False


class GenMethod(Method):
    """새로 생성하는 메서드. 반드시 common.generate.Runner 로 생성하고
    common.scoring.make_scorer 로 채점한다."""
    needs_gpu = True

    def __init__(self, bench, runner):
        super().__init__(bench)
        self.runner = runner
