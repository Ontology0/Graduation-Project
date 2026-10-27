"""팀원 배정용 SOTA 스텁. 각자 맡은 논문을 아래 클래스에 채운다.

구현 규칙
  1. common/ 은 고치지 않는다.
  2. 생성은 common.generate.Runner 로만 한다(프롬프트·배치·EOS 가 A0 와 같아야 한다).
  3. 채점은 common.scoring.make_scorer 로만 한다.
  4. 학습이 필요하면 bench.fold 로 5-fold, test fold 를 보지 않는다.
  5. run() 은 (em 벡터, pred 문자열 목록) 을 반환한다.

배정 제안
  1순위 SpARE : 우리와 같은 채점 방향 + training-free + 중간층 표상 + Llama3-8B.
                여기서 못 이기면 기여가 성립하지 않는다.
  2순위 SHIFT : 학습 기반. 성능 절대치 비교용. 우리는 training-free / 비용 축으로 포지션.
  3순위 COIECD / CoCoA : context-faithful 계열. 설정 차이 입증용.
"""
from __future__ import annotations

from .base import GenMethod, register


@register("spare")
class SpARE(GenMethod):
    """Steering Knowledge Selection Behaviours in LLMs via SAE-Based
    Representation Engineering (Zhao et al., NAACL 2025 long 264).
    github.com/yuzhaouoe/SAE-based-representation-engineering

    착수 전 확인 — 여기서 막히면 다른 실험에도 영향이 간다
      사전학습 SAE 가 Llama-3.1-8B 용으로 있는지. 없으면 백본을 Llama-3-8B 로
      바꿔야 하는데, 그러면 A0/A1 기준선을 전부 다시 측정해야 한다.

    구현 메모
      - 중간층 residual 에 기능 feature 를 더하는 training-free 개입.
        우리 w_v3 steering 과 개입 위치가 거의 같아 직접 비교 가능하다.
      - 주입은 common.generate 의 Runner.steer 를 그대로 쓴다
        (vec={층: 벡터}, scale={층: 크기}). 훅을 새로 달지 않는다.
      - 'use memory' 모드가 우리 retain 방향에 대응한다. 'use context' 는 반대 방향.
        두 모드 모두 돌려 양쪽 수치를 싣는다.
    """
    paper = "SpARE (NAACL 2025)"
    family = "conflict-resolution"

    def run(self):
        raise NotImplementedError("SpARE: SAE 로드 + feature 선정 + 주입을 여기에 구현")


@register("shift")
class SHIFT(GenMethod):
    """SHIFT: Gate-Modulated Activation Steering (arXiv 2606.27786).
    FFN 활성에 learnable gate, backbone 고정, 학습 파라미터 0.01% 미만.

    메모: 학습이 필요하므로 train fold 로만 학습한다.
          성능 절대치로 붙으면 불리할 수 있다. 비교 축은 training-free / 추론 비용.
    """
    paper = "SHIFT (2026)"
    family = "conflict-resolution"

    def run(self):
        raise NotImplementedError


@register("coiecd")
class COIECD(GenMethod):
    """COIECD (Yuan et al., 2024). 토큰별 충돌 판정 기반 제약적 디코딩."""
    paper = "COIECD (2024)"
    family = "context-faithful"

    def run(self):
        raise NotImplementedError


@register("cocoa")
class CoCoA(GenMethod):
    """CoCoA. 문맥/파라메트릭 분포 결합 디코딩."""
    paper = "CoCoA"
    family = "context-faithful"

    def run(self):
        raise NotImplementedError
