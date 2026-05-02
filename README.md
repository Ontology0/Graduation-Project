# Alltology

> AWS가 상용 인프라로 검증한 OWL 기반 지식 파이프라인을 오픈소스로 재현하고,
> Fine-tuning과 결합하여 **융합 방법론의 유효성을 실증적으로 검증한다**

<br/>

## 저장소 상태 (research scaffold)

이 저장소는 **research scaffold** 단계입니다. 벤치마크, 데이터셋, 평가 프로토콜은 **아직 미정**이며, `data/`, `doc/`, `eval/`, `finetuning/`, `rag/`, `results/`에는 각 폴더 목적을 적은 `README.md`가 있습니다. **실제로 실행 가능한 코드는** `rag/pipeline_stub.py`, `finetuning/train_stub.py`, `eval/evaluate_stub.py` **placeholder뿐**이며, 외부 API 호출·학습·점수 산출은 하지 않습니다.

<br/>

## 🧭 프로젝트 개요

LLM의 할루시네이션 문제를 해결하는 두 가지 접근—**파라미터 학습(Fine-tuning)** 과 **외부 지식 증강(RAG)**—을 동일한 벤치마크 위에서 실증 비교하고, 융합했을 때 시너지가 발생하는지 검증합니다.

AWS가 상용 인프라로 구현한 OWL 기반 파이프라인을 오픈소스 스택으로 재현하고, **LLM API 기반 온톨로지 자동 추출**을 추가해 자동화한 것이 본 연구의 핵심 기여입니다.

<br/>

## 🚨 문제

LLM은 강력하지만, **학습 시점 이후의 지식**이나 **도메인 특화 정보**에서는 한계가 있습니다.
이를 해결하는 방식은 두 갈래로 나뉩니다.

|  | 방식 | 한계 |
|---|---|---|
| 내부 접근 | 모델을 직접 학습시킨다 (Fine-tuning) | 비용이 크고, 학습한 것을 잊는다 |
| 외부 접근 | 필요한 지식을 찾아서 넣어준다 (RAG) | 추론 일관성의 한계 |

**어느 쪽이 더 나은지, 합치면 더 좋아지는지 — 체계적으로 비교하고 융합한 연구는 아직 충분하지 않습니다.**

<br/>

## 💡 솔루션

```mermaid
flowchart LR
    A[기존 연구\n둘 중 하나만] -->|한계| B[실증적 답 없음]
    B --> C[우리 연구\n셋 다 비교]
    C --> D[방법 A\n학습만]
    C --> E[방법 B\n지식 주입만]
    C --> F[방법 C\n융합]
```

<br/>

## 🤖 기술 파이프라인

```mermaid
flowchart TD
    subgraph OFF["사전 준비 (오프라인)"]
        A[도메인 문서 / 텍스트]
        B[LLM API\nOWL 온톨로지 자동 추출]
        C[Apache Jena Fuseki\nRDF 트리플 저장 + SPARQL]
        D[OpenSearch\n벡터 인덱싱]
        A --> B --> C --> D
    end
    subgraph ON["런타임 (온라인)"]
        E[검색 쿼리 입력]
        F["1. Retrieval\nOpenSearch → 관련 트리플 추출"]
        G["2. Augmented Generation\n트리플 + 쿼리 → LLM API 호출"]
        H[응답 생성]
        E --> F --> G --> H
    end
    D -->|쿼리 들어옴| E
```

<br/>

## 🧪 실험 설계

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

### 핵심 연구 질문

1. Fine-tuning과 RAG 중 어느 쪽이 할루시네이션 감소에 더 효과적인가?
2. 두 기법을 융합했을 때 성능이 단순 합산 이상으로 향상되는가?
3. 도메인 특성(미디어)에 따라 최적 전략이 달라지는가?

<br/>

## 📊 AWS 원본 vs 우리 구현

| AWS 원본 | 우리 (오픈소스) | 비고 |
|---|---|---|
| 수동 OWL 설계 | LLM API 자동 추출 | **추가 기여** |
| Amazon Neptune | Apache Jena Fuseki | 무료 오픈소스 |
| 상용 검색 인프라 | OpenSearch | 무료 오픈소스 |
| 상용 LLM | LLM API | 오픈소스 모델 |
| 상용 Fine-tuning | LoRA / PEFT | 무료 오픈소스 |

<br/>

## 📚 Related Work

| 연구 | 방법 | 한계 |
|---|---|---|
| LoRA (Hu et al., 2022) | 파라미터 효율적 Fine-tuning | 외부 지식 구조 미반영 |
| RAG (Lewis et al., 2020) | 비구조적 문서 검색 증강 | 온톨로지 논리 추론 불가 |
| LLMs4OL (Babaei et al., 2023) | LLM 기반 온톨로지 자동 학습 | Fine-tuning과의 융합 미검증 |
| OntoTune (WWW 2025) | 온톨로지 기반 LLM self-training | 파라미터 학습과 분리된 접근 |
| GraphGen (2025) | KG → Fine-tuning 데이터 자동 생성 | 온톨로지 구조적 추론 미활용 |
| AWS Neptune + OWL (2022) | 상용 인프라 기반 OWL 파이프라인 | LLM 증강 · Fine-tuning 미결합 |

**본 연구의 기여:** 오픈소스 스택으로 파이프라인을 재현하고, 내부 / 외부 / 융합 세 방식을 벤치마크 기반으로 실증 비교하여 융합 방법론의 유효성을 검증합니다.

<br/>

## 🛠 기술 스택

### AI / 학습

| 역할 | 기술 |
|------|------|
| Fine-tuning | ![LoRA](https://img.shields.io/badge/LoRA/QLoRA-PEFT-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white) |
| Alignment | ![DPO](https://img.shields.io/badge/DPO-Alignment-412991?style=for-the-badge&logo=openai&logoColor=white) |
| 개발 환경 | ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) ![HuggingFace](https://img.shields.io/badge/HuggingFace_TRL-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black) |
| Testing | ![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) |

### 지식 증강 (RAG / 온톨로지)

| 역할 | 기술 |
|------|------|
| 온톨로지 저장 | ![Jena Fuseki](https://img.shields.io/badge/Apache_Jena_Fuseki-E25A1C?style=for-the-badge&logo=apache&logoColor=white) |
| 벡터 검색 | ![OpenSearch](https://img.shields.io/badge/OpenSearch-005EB8?style=for-the-badge&logo=opensearch&logoColor=white) |
| OWL 추출 | ![LLM API](https://img.shields.io/badge/LLM_API-OWL_Auto_Extract-412991?style=for-the-badge&logo=openai&logoColor=white) |

### 평가

| 역할 | 기술 |
|------|------|
| 자동 평가 | ![RAGAS](https://img.shields.io/badge/RAGAS-Faithfulness-00A896?style=for-the-badge) |
| 정성 평가 | ![LLM-as-a-judge](https://img.shields.io/badge/LLM--as--a--judge-GPT4-412991?style=for-the-badge&logo=openai&logoColor=white) |

### 공통

| 역할 | 기술 |
|------|------|
| 버전 관리 | ![Git](https://img.shields.io/badge/Git-F05033?style=for-the-badge&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-121011?style=for-the-badge&logo=github&logoColor=white) |

<br/>


| 모듈 | 실행 (placeholder) | 비고 |
|:--:|:--|:--|
| **RAG** | `python rag/pipeline_stub.py` | 인터페이스만; 검색·생성 없음 |
| **Fine-tuning** | `python finetuning/train_stub.py` | 인터페이스만; 학습 없음 |
| **Eval** | `python eval/evaluate_stub.py` | 인터페이스만; 점수 없음 |
| **테스트** | | 스캐폴드 단계에서 `pytest` 스위트는 아직 없을 수 있음 |

<br/>

## 📁 저장소 구조

```text
Graduation-Project/
├── data/          # 데이터·전처리 산출물 (벤치마크 확정 후)
├── doc/           # 연구 문서, 설계 초안, 회의·결정 기록
├── eval/          # 평가 스크립트 예정 (프로토콜 미정)
├── finetuning/    # LoRA/QLoRA 등 학습 코드 예정
├── ontology/ 
├── rag/           # RAG 베이스라인 예정 (현재 stub만)
├── results/       # 실험 산출물 (실제 결과 없음; 날짜별 폴더 예정)
├── .env.example
├── CNAME
├── index.html
├── README.md
├── CLAUDE.md
└── requirements.txt
```

### 처음 보는 사람을 위한 읽는 순서

1. 위 **저장소 상태**와 각 폴더 `README.md`로 스캐폴드 범위를 확인한다.
2. `doc/`에서 연구 방향·회의록·초안을 읽는다.
3. `rag/pipeline_stub.py`, `finetuning/train_stub.py`, `eval/evaluate_stub.py`로 향후 코드 진입점 형태만 본다.
4. 벤치마크와 프로토콜이 확정되면 `data/`, `eval/`, `results/`가 채워진다.

<br/>

## 🌿 브랜치 전략

```
main ← 최종 제출 / 논문 기준
 └── dev ← 통합 개발 (PR 타겟)
      ├── feat/ontology/#이슈번호-설명
      ├── feat/rag/#이슈번호-설명
      ├── feat/finetuning/#이슈번호-설명
      └── fix/#이슈번호-설명
```

<br/>

## 👥 팀

**팀명:** Alltology · **트랙:** 연구 · **지도교수:** 황의원 교수님

| <img src="https://github.com/ryeong03.png" width="120" /> | <img src="https://github.com/bbberylll.png" width="120" /> | <img src="https://github.com/dev-ldy03.png" width="120" /> |
|:--:|:--:|:--:|
| **박세령** | **손현경** | **이다영** |
| 온톨로지 설계 · RAG 파이프라인 | AI 엔진 · 파인튜닝 (LoRA/QLoRA) | 개발 · 데이터 파이프라인 |
| [@ryeong03](https://github.com/ryeong03) | [@bbberylll](https://github.com/bbberylll) | [@dev-ldy03](https://github.com/dev-ldy03) |

<br/>

<div align="center">
<sub>이화여자대학교 졸업프로젝트 2026</sub>
</div>
