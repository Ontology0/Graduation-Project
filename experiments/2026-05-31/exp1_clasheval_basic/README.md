# exp1 — ClashEval 기본 (거짓 문서 판별)

## 목적
검색된 문서가 거짓 정보를 담고 있을 때, 모델이 거짓 문서를 거부하고
자신의 지식으로 정답을 내는가. Base RAG vs Conflict-aware prompting 비교.

## 설계
- 모델: gpt-4o-mini (OpenAI API)
- 데이터: 24케이스 (doc_correct 12 + doc_false 12)
  - doc_correct: 문서가 옳음 (모델 상식보다 최신/정확)
  - doc_false: 문서가 거짓 (유명 사실을 틀리게)
- 문서: contextual 문서 1개 + distractor

## 결과
| | Base | Conflict-aware |
|---|---|---|
| 전체 정답률 | 75% (9/12)* | 100% (12/12)* |
| doc_correct 정답 | 6/6 | 6/6 |
| doc_false 정답 | 3/6 | 6/6 |

(*초기 12케이스 버전 기준)

- doc_correct(문서 옳음): 두 arm 모두 정답
- **doc_false(문서 거짓): Base 3/6 속음, Conflict-aware 6/6 거부**

## 해석
프롬프트만 바꿔도 거짓 문서 거부(robustness)가 크게 개선됨.
단, 이 시점에서는 "문서밖에 단서가 없을 때"의 행동만 본 것이라
정답 문서가 있으면 어떻게 되는지는 exp2에서 분해.

## 파일
- `build_dataset.py` : 데이터 생성기 (시드 + GPT 확장 옵션)
- `clash_conflicts.jsonl` : 데이터
- `run_clasheval.py` : 실험 + 자동 채점
- `results/` : 실행 결과
