# exp3 — Temporal Update (명시적 충돌)

## 목적
본 연구의 메인 RQ에 정렬: 내부(parametric) 지식이 오래되고
외부(contextual) 검색이 최신일 때, 모델이 옛 지식을 고집하는가
vs 최신 정보로 업데이트하는가.

## 설계
- 모델: claude-haiku-4-5 (LiteLLM)
- 데이터: 실제 세계의 최근 변화 10건
  (Twitter→X, 영국 군주 교체, 최다 인구국 China→India 등)
- parametric=옛 값, contextual=최신 값, gold=최신
- **문서가 변화를 명시적으로 설명** ("In 2023, Twitter was rebranded as X")

## 측정
- update_rate: 최신값 채택 비율 (= 정답)
- stuck_rate: 옛값 고집 비율

## 결과
| | Base | Conflict-aware |
|---|---|---|
| update_rate | 100% | 100% |
| stuck_rate | 0% | 0% |

verdict 분포: 대부분 mixed("예전엔 X였으나 지금은 Y") — 변화를 명시하며 업데이트.

## 해석
두 arm 모두 100%. 문서가 변화를 직접 설명하므로 모델이 충돌을
추론할 필요 없이 그대로 수용함. → 충돌이 너무 약했음.
진짜 충돌(문서가 변화를 설명하지 않는 경우)은 exp4에서 측정.

## 파일
- `build_temporal.py` : 명시적 temporal 데이터 생성기
- `temporal_conflicts.jsonl` : 10케이스
- `run_temporal.py` : 실험 + 채점
