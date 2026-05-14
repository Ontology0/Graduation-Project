# PA-RAG 논문

> Wu et al., NAACL 2025 | arXiv:2412.14510
> "RAG Alignment via Multi-Perspective Preference Optimization"

---


> 일반 LLM을 RAG에 최적화하기 위해 SFT → DPO 순차 학습을 제안한 논문.
> 정보성, 강건성, 인용 품질 세 관점에서 단계적으로 모델을 정렬함.

---

## 문제 정의

일반 LLM을 RAG 생성기로 쓰면 세 가지 문제가 생김

| 문제 | 설명 |
|---|---|
| 정보성 부족 | 검색 문서를 충분히 활용하지 못하고 일부를 무시함 |
| 강건성 부족 | 노이즈 문서(관련 없는 문서)에 흔들려 틀린 답을 냄 |
| 인용 품질 부족 | 출처를 잘못 인용하거나 관련 없는 문서를 인용함 |

기존 해결 방식의 한계

```
SFT만 쓰는 방식  → RAG의 다양한 상황을 전부 커버 못함
파이프라인 방식  → 추가 단계가 많아져 비용 증가, 일부 요구사항만 해결
```

---

## 제안 방법 — PA-RAG

학습을 두 단계로 나눔

### 1단계 — SFT (기초 능력 학습)

ChatGPT-3.5로 고품질 응답을 생성하고 Citation Rewrite 메커니즘으로
인용 품질을 검증해 학습 데이터를 만듦

```
데이터 구성 과정

기존 QA 데이터셋
    ↓
상위 100개 문서 검색 → 정답 포함 문서(Golden Docs) 최대 5개 선별
    ↓
ChatGPT-3.5로 응답 생성
    ↓
Citation Rewrite 3단계
  Step 1. 인용 검증 (NLI 모델로 인용-주장 일치 확인)
  Step 2. 인용 보정 (검증 실패 시 가능한 인용 조합 탐색)
  Step 3. 인용 단순화 (불필요한 인용 제거)
    ↓
SFT 학습 데이터 완성 (총 58,858개)
```

### 2단계 — DPO (선호도 최적화, 3개 서브스테이지)

각 관점마다 (chosen, rejected) 쌍을 만들어 순차적으로 학습

**서브스테이지 1 — 정보성 최적화 (Response Informativeness)**
```
목표: 문서를 빠짐없이 활용하게 만들기

chosen:   모든 Golden Docs를 준 경우의 완전한 답변
rejected: 일부 Golden Docs를 제거한 경우의 불완전한 답변
```

**서브스테이지 2 — 강건성 최적화 (Response Robustness)**
```
목표: 노이즈 문서를 무시하게 만들기

노이즈 문서 2종류:
  - 관련은 있지만 답 없는 문서 (2개)
  - 아예 관련 없는 문서 (2개)

chosen:   노이즈 없는 환경의 완전한 답변
rejected: 노이즈 포함 환경에서 불완전한 답변
```

**서브스테이지 3 — 인용 품질 최적화 (Citation Quality)**
```
목표: 정확한 문서만 인용하게 만들기

chosen:   Citation Rewrite로 교정된 정확한 인용
rejected: NLI 검증 실패한 잘못된 인용
```

---

## 실험 설계

### 데이터셋

| 용도 | 데이터셋 |
|---|---|
| 학습 | ASQA, WebQuestions, Natural Questions |
| 평가 (학습에 포함) | ASQA, WebQuestions, Natural Questions |
| 평가 (미학습, 일반화 검증) | TriviaQA |

### 베이스 모델

```
LLAMA2-7B-CHAT
LLAMA2-13B-CHAT
LLAMA3-8B-INSTRUCT
```

### 평가 지표

```
정확도:    EM (Exact Match)     — 정답이 응답에 포함되는지
인용 품질: Citation Recall      — 인용이 답변을 충분히 지지하는지
           Citation Precision   — 불필요한 문서를 인용하지 않는지
```

### 비교 베이스라인

```
① Base Generator     일반 LLM, 파인튜닝 없음
② RetRobust-13B      SFT로 강건성만 높인 모델
③ Self-RAG-13B       랭킹 후 생성하는 파이프라인 방식
④ SFT on Chosen      DPO 없이 chosen 데이터로만 SFT한 모델
```

### 실험 환경

```
GPU: A800 80G × 4
Memory: 1TB
Fine-tuning: Full Fine-tuning
```

---

## 실험 결과

### 메인 결과

PA-RAG가 모든 모델, 모든 데이터셋에서 베이스라인을 압도함

```
평균 성능 향상 (Base Generator 대비)
  EM 정확도:          +13.97%
  Citation Recall:    +49.77%
  Citation Precision: +39.58%
```

### 단계별 기여도 분석 (Ablation Study)

각 학습 단계가 모두 유의미하게 기여함

| 학습 단계 | 설명 | 효과 |
|---|---|---|
| IFT | SFT 기초 학습 | 기초 성능 확보 |
| IFT + RI | 정보성 DPO 추가 | 정확도 향상 |
| IFT + RI + RR | 강건성 DPO 추가 | 강건성 향상 |
| IFT + RI + RR + CQ | 인용 품질 DPO 추가 | 최고 성능 달성 |

### 학습 순서의 중요성

```
RI → RR 순서  -> 성능 최고
RR → RI 순서  -> 성능 저하
동시 학습      -> 성능 저하
```

이유: 정보성(문서 활용)이 기초 능력, 강건성(노이즈 제거)이 고급 능력이기 때문.
기초부터 쌓아야 함 → **커리큘럼 학습(Curriculum Learning) 효과**

### SFT vs DPO 비교

```
SFT로 RI → RR 순차 학습:
  두 번째 학습에서 첫 번째 학습 내용을 잊어버림
  → Catastrophic Forgetting 발생

DPO로 RI → RR 순차 학습:
  두 번 학습해도 성능이 꾸준히 향상됨
  → 상충되는 목표를 동시에 잘 다룸
```

---

## 논문의 한계 (Limitations)

논문 자체에서 명시한 한계

```
① 학습 스테이지가 4단계(SFT + DPO×3)라
   하이퍼파라미터 탐색이 복잡하고 번거로움

② Full Fine-tuning 방식이라 GPU 자원 요구가 큼
   실험 환경: A800 80G GPU × 4, 메모리 1TB
```

---

## 우리팀 연구와의 연결 포인트

| PA-RAG의 한계 | 우리가 채울 수 있는 것 |
|---|---|
| Full Fine-tuning (고비용) | LoRA / QLoRA로 경량화 → RTX 3090 × 4에서 재현 가능 |
| 지식 충돌 시나리오 학습 없음 | ClashEval 기반 충돌 케이스를 DPO 데이터에 명시적으로 포함 |
| 비구조적 텍스트 검색 | OWL 온톨로지 기반 구조화 검색으로 노이즈 자체를 줄임 |
| Attention 분석 없음 | Attention Map으로 충돌 시 모델 행동 시각화 및 근거 제시 |

---

## 참고 링크

- 논문 원문: https://arxiv.org/abs/2412.14510
- 공식 코드 및 데이터셋: https://github.com/wujwyi/PA-RAG
