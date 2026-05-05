# 일반 벤치마크를 활용한 LLM 내부 파라미터 확장과 온톨로지 기반 지식 증강 기법의 실증적 성능 비교 및 융합 방법론 연구

> 부제: 단계적 Fine-tuning과 온톨로지 기반 외부 지식 검색의 결합(RAG)이 LLM 성능에 미치는 영향

---

## 문제

LLM은 강력하지만, 특정 도메인에서는 **틀린 답을 자신 있게 말한다**

이를 해결하는 방식은 두 갈래로 나뉜다

| | 방식 | 한계 |
|---|---|---|
| 내부 접근 | 모델을 직접 학습시킨다 (Fine-tuning) | 비용이 크고, 학습한 것을 잊는다 |
| 외부 접근 | 필요한 지식을 찾아서 넣어준다 (RAG) | 추론 일관성의 한계 |

**어느 쪽이 더 나은지, 합치면 더 좋아지는지 — 실증적 답이 없다**

---

## 해결 아이디어

```mermaid
flowchart LR
    A["기존 연구 둘 중 하나만"] -->|한계| B[실증적 답 없음]
    B --> C["우리 연구: 셋 다 비교"]
    C --> D["방법 A 학습만"]
    C --> E["방법 B 지식 주입만"]
    C --> F["방법 C 융합"]
```

AWS가 상용 인프라로 구현한 파이프라인을 참고하되
**누구나 쓸 수 있는 오픈소스로 재현**하고, **온톨로지 자동 추출**을 추가해 자동화한다

---

## 기술 파이프라인

```mermaid
flowchart TD
    subgraph OFF["사전 준비 (오프라인)"]
        A[도메인 문서 / 텍스트]
        B["LLM API로 OWL 온톨로지 자동 추출"]
        C["Apache Jena Fuseki : RDF 트리플 저장 + SPARQL"]
        D["OpenSearch 이용해 벡터 인덱싱"]
        A --> B --> C --> D
    end

    subgraph ON["런타임 (온라인)"]
        E[검색 쿼리 입력]
        F["1. Retrieval : OpenSearch → 관련 트리플 추출"]
        G["2. Augmented Generation : 추출된 트리플 + 쿼리 → LLM API 호출"]
        H[응답 생성]
        E --> F --> G --> H
    end

    D -->|쿼리 들어옴| E
```

---

## 실험 설계

```mermaid
flowchart LR
    subgraph A["방법 A — 내부 (파라미터)"]
        A1[벤치마크 데이터] --> A2[1차 Fine-tuning] --> A3[2차 Fine-tuning] --> A4[성능 측정]
    end

    subgraph B["방법 B — 외부 (지식 증강)"]
        B1[도메인 문서] --> B2[OWL 자동 추출] --> B3[RAG 파이프라인] --> B4[성능 측정]
    end

    subgraph C["방법 C — 융합 (우리 연구)"]
        C1[A + B 결합] --> C2[성능 측정]
    end

    A4 & B4 & C2 --> Z[A vs B vs C 실증 비교]
```

---

## AWS 버전 vs 본 연구

| AWS 버전 | 본 연구 (오픈소스) | 비고 |
|---|---|---|
| 수동 OWL 설계 | **LLM API 자동 추출** | 추가 기여 |
| Amazon Neptune | Apache Jena Fuseki | 무료 오픈소스 |
| 상용 검색 인프라 | OpenSearch | 무료 오픈소스 |
| 상용 LLM | LLM API | 오픈소스 모델 |
| 상용 Fine-tuning | LoRA / PEFT | 무료 오픈소스 |

---

## Related Work

| 연구 | 방법 | 한계 |
|---|---|---|
| PA-RAG (NAACL 2025) | RAG의 정보성·강건성·인용 품질을 위해 SFT와 DPO를 순차 적용하는 멀티스테이지 학습 | Full Fine-tuning 중심이라 비용·규모 부담이 크고, 온톨로지·구조화 지식 파이프라인과의 융합 실증은 다루지 않음 |
| ClashEval (2024) | Parametric(내부) 지식과 Contextual(검색) 문서가 충돌할 때 모델 반응을 유형별로 실험·측정 | Knowledge Conflict의 현상 분석에 초점; 해결 방법론이나 내부·외부·융합 세 방식의 체계적 비교는 아님 |
| DPA-RAG (WWW 2025) | Retriever–Generator 간 선호 간극을 줄이기 위한 Dual Alignment(SFT, reranker 정렬 + pre-aligned 단계) | 검색–생성 정렬에 집중; OWL 온톨로지 기반 지식 증강과 LoRA 등 경량 파인튜닝을 결합한 파이프라인 실증과는 초점이 다름 |



**본 연구의 기여**
오픈소스 스택으로 파이프라인을 재현하고, 내부 / 외부 / 융합 세 방식을 벤치마크 기반으로 실증 비교하여 융합 방법론의 유효성을 검증한다
