# 공유 데이터 정본 (exp5 / exp6)

3인이 동일 데이터로 실험하기 위한 정본 파일. **각자 재추출 금지.**

## 파일

| 파일 | n | 용도 | sha256 |
|---|---|---|---|
| cbqa_sample_n1000_seed42.jsonl | 1000 | exp5 (ConflictBank 데이터 감사) | `06293de4d4a08394d5eb431acf0efd613e806b457ad750da767111f60df68d4c` |
| exp6_questions_n300_seed42.jsonl | 300 | 중간 산출물 (직접 사용 금지) | `7fa8ee9979733ec7d971c16949c0983ef60dfcd5cb7f3f9ab76e2d4b20409387` |
| **exp6_questions_n400_seed42.jsonl** | 400 | **exp6 실험 정본** | `963aa84bfb04b5f1fea2295c5e4ff9744e8a287899a0d9eb154c9467c92ac920` |
| meta_exp5.json | — | 생성 메타데이터 (seed, 버전, 타임스탬프) | — |

## 데이터 계보

- **CB**: `Warrieryes/CB_qa` train (553,117행) → seed=42 shuffle → n=1000 → dedup → seed=42 → n=300
  - `gold`는 `object` 필드 사용 (객관식 options는 미사용, 자유 생성 채점)
- **TQA**: `mandarjoshi/trivia_qa` rc.nocontext validation (17,944행) → seed=42 → n=100
  - aliases 필드 내장 (건당 약 30개)
- n400 = CB 300 + TQA 100, `source` 필드로 구분

## TriviaQA 100건을 넣은 이유

CB_qa는 Wikidata 롱테일 엔티티 중심이라 closed-book 정답률이 낮을 것으로 예상됨.
정답군이 극소수면 AUROC의 신뢰도가 무너지므로, 정답군 앵커로 TriviaQA를 추가.
TriviaQA는 confidence 측정 선행 연구(semantic entropy 계열)의 표준 벤치마크이기도 함.

분석 시 전체 AUROC와 함께 **분포별(CB vs TQA) AUROC를 각각 보고**한다.

## 사용 규칙

1. 이 파일만 사용. 각자 스크립트로 재추출 금지 (라이브러리 버전에 따라 셔플 결과가 달라짐)
2. 실험 노트북 첫 셀에서 해시 검증 필수:

```python
import hashlib
EXPECTED = "963aa84bfb04b5f1fea2295c5e4ff9744e8a287899a0d9eb154c9467c92ac920"
p = "experiments/main_2026-07-11/shared_data/exp6_questions_n400_seed42.jsonl"
assert hashlib.sha256(open(p, "rb").read()).hexdigest() == EXPECTED, "데이터 버전 불일치!"
print("데이터 검증 OK")
```

3. 모델별 담당: Llama-3.1-8B / Qwen2.5-7B-Instruct / Mistral-7B-Instruct-v0.3
   — 질문셋은 동일, 모델만 변인