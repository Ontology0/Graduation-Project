## 1. Related Work 분석

연구 주제인 'RAG-alignment 및 Knowledge Conflict 해결'과 밀접한 3가지 핵심 연구를 선정

### 논문 1: PA-RAG (NAACL 2025)
* **핵심 내용:** 일반 목적 LLM의 RAG 수행 시 발생하는 정보성(Informativeness - 검색 문서 활용도의 문제), 강건성(Robustness - 노이즈 문서 대응 문제), 인용 품질(Citation Quality - 출처 인용의 문제) 부족 문제를 지적.
* **방법론:** SFT와 DPO를 순차적으로 적용하는 **멀티스테이지 학습**을 통해 기초 능력(문서 활용 능력)부터 쌓고 고급 능력(노이즈 제거)를 나중에 학습하는 커리큘럼 학습 효과가 있음.
* **벤치마크:** ASQA, WebQuestions, Natural Questions, TriviaQA
* **모델:** Llama2-7b, Llama2-13b, Llama3-8b
* **학습 방식:** Full Fine-tuning
* **본 연구와의 연계:** RAG-aware DPO 아이디어의 기초가 되었으며, 단계별 학습의 효용성을 참고하였음.

### 논문 2: ClashEval (2024)
* **핵심 내용:** RAG 시스템에서 모델의 내부 지식(Parametric)과 검색된 외부 문서(Contextual)가 충돌할 때 모델이 어떻게 행동하는지를 실험적으로 측정해 분석한 논문.
* **핵심 발견:** 강한 모델조차 틀린 문서를 맹목적으로 따르거나, 반대로 맞는 문서를 무시하는 현상을 유형별(Type A, B, C)로 정의.
* **본 연구와의 연계:** "왜 RAG 최적화가 필요한가"에 대한 강력한 동기를 부여하며, 우리 연구에서 해결하고자 하는 **Knowledge Conflict**의 실증 근거가 됨.

### 논문 3: DPA-RAG (WWW 2025)
* **핵심 내용:** 검색기(Retriever)와 생성기(Generator) 사이의 '선호도 간극(Knowledge Preference Gap)'을 문제로 정의. 즉, retriever가 가져오는 문서와 LLM이 실제로 필요로 하는 문서가 다름.
* **방법론:** 검색기와 생성기를 동시에 정렬하는 **Dual Alignment**를 제안함. 내부 정렬(External Alignment)로는 reranker에 pairwise, pointwise, contrastive preference alignment를 통합하고, 내부 정렬(Internal Alignment)로는 SFT 이전에 pre-aligned 단계를 도입해 LLM이 자신의 추론 선호도에 맞는 지식을 내재화 하도록 함.
* **벤치마크:** NQ, TriviaQA, HotpotQA, WebQuestions
* **학습 방식:** SFT 기반 (DPO 아님)
* **본 연구와의 연계:** 생성기뿐만 아니라 파이프라인 전체의 정렬 중요성을 시사하며, 우리 연구와 생성기 집중도 측면에서 대조군 역할을 함.

---

## 2. 우리 팀 연구의 차별성

| 항목 | PA-RAG | ClashEval | DPA-RAG | **우리 팀 연구 (Proposed)** |
| :--- | :---: | :---: | :---: | :--- |
| **핵심 기여** | Generator DPO 정렬 | 충돌 현상 실증 | Dual Alignment | **LoRA 경량화 + 충돌 해결** |
| **Fine-tuning** | Full FT | 없음 | SFT | **LoRA / QLoRA (효율성)** |
| **Knowledge Conflict** | X (일부 고려) | O (현상 제기만) | X | **O 명시적 학습 및 해결** |
| **실무적 접근** | 고비용 학습 | 분석 위주 | 복합 정렬 | **저비용 고효율 파이프라인** |

### [우리 팀만의 해석과 전략]
1.  **실질적인 문제 해결:** ClashEval이 제기한 '지식 충돌 시나리오'를 단순 분석에 그치지 않고, 이를 **DPO 학습 데이터셋에 명시적으로 포함**하여 모델이 스스로 정보를 비판적으로 수용하게끔 만듦.
2.  **경량화 및 효율성:** Full Fine-tuning 위주인 기존 연구와 달리, **RTX 3090 × 4** 환경에 최적화된 **LoRA/QLoRA** 기법을 적용하여 학부 졸프 수준에서도 재현 가능한 고효율 연구 모델을 지향함.
3.  **케이스 스터디 기반 검증:** 단순히 벤치마크 점수만 높이는 것이 아니라, 구체적인 지식 충돌 케이스를 설정하여 우리 모델이 어떻게 논리적으로 반응하는지 정성적으로 증명할 것임.

---
