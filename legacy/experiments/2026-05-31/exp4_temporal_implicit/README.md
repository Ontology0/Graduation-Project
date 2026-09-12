# exp4 — Temporal Update (암묵적 충돌)

## 목적
exp3에서 문서가 변화를 직접 설명해 충돌이 약했던 한계를 보완.
문서가 변화를 설명하지 않고 **최신 사실을 당연한 듯 전제**하게 하여,
모델이 내부 지식과의 충돌을 스스로 감지해야 하는 상황을 만든다.

## 설계
- 모델: claude-haiku-4-5 (LiteLLM)
- 데이터: exp3와 같은 실제 변화 10건, 단 문서 표현을 암묵적으로 변경

| 모드 | 문서 예시 |
|---|---|
| 명시적 (exp3) | "In 2023, Twitter was rebranded as X" (변화 설명) |
| 암묵적 (exp4) | "X rolled out a new subscription tier" (X를 전제, 설명 없음) |

질문도 정답 힌트가 없도록 중립적으로 작성.

## 결과
| | Base | Conflict-aware |
|---|---|---|
| update_rate | 100% | 100% |
| stuck_rate | 0% | 0% |

verdict 분포: updated(최신만 언급)가 증가 — 문서가 변화를 설명하지 않으니
모델도 옛값 언급 없이 최신값만 답하는 경향.

## 해석
암묵적으로 충돌을 강화했음에도 두 arm 모두 100%.
→ **강한 모델(Claude haiku)은 temporal conflict를 프롬프트 도움 없이도
거의 완벽히 해결한다 (천장 효과).**

이는 본 연구의 방향을 명확히 한다:
- 강한 모델 = upper bound (이미 잘함)
- 차이가 나는 것은 약한 모델 / 본 연구 대상 Llama 3.1-8B
- → 다음 단계는 Llama-8B로 동일 실험하여 baseline 측정

## 파일
- `build_temporal_implicit.py` : 암묵적 temporal 데이터 생성기
- `temporal_implicit_conflicts.jsonl` : 10케이스
- `run_temporal_implicit.py` : 실험 + 채점
