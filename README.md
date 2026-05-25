# 검색 결과와 내부 지식이 충돌할 때: Preference Learning 기반 RAG 정렬 연구
## Conflict-Aware PA-RAG

> **주제:** LLM Knowledge Conflict 완화를 위한 RAG–Fine-tuning 융합 연구  
> PA-RAG의 정렬 기준(informativeness, robustness, citation quality)을 확장하여, **internal knowledge와 external evidence가 충돌하는 상황**을 DPO + LoRA로 내재화할 수 있는지 탐구.

<br/>

## 저장소 상태 (research scaffold)

- **This repository is currently a research scaffold.**
- Implementation, training, and evaluation results will be updated progressively.
- **No final experimental results are reported yet.**
- 실행 가능한 코드는 `rag/pipeline_stub.py`, `finetuning/train_stub.py`, `eval/evaluate_stub.py` **placeholder**뿐이며, 외부 API 호출·학습·점수 산출은 하지 않음.
- 벤치마크, 데이터셋, 평가 프로토콜은 **확정 중**입니다. 상세 초안은 `docs/`를 참고.

<br/>

## 연구 범위

본 연구는 knowledge conflict 중에서도 **context–memory conflict**를 다룸.

| 용어 | 정의 | 본 연구 |
|------|------|:------:|
| **Context–memory conflict** | RAG에서 검색된 **external context**와 LLM **internal(parametric) knowledge**가 서로 다른 답을 가리키는 상황 | **핵심 범위** |
| Inter-context conflict | 여러 검색 문서·문맥 간 상호 모순 | 메인 연구 대상 **아님** (벤치마크 참고 수준 가능) |
| Intra-memory conflict | 파라미터 지식 내부의 자기 모순 (검색 없이) | 메인 연구 대상 **아님** |

<br/>

## 연구 문제

RAG가 검색 문서를 제공하더라도 LLM이 **내부 지식에 의존해 다른 답**을 생성할 수 있다. 반대로, 신뢰할 수 없는 검색 결과를 맹목적으로 따를 수도 있다.

| 충돌 상황 | 바람직한 행동 | 현재 문제 |
|---|---|---|
| 외부 문서가 최신·권위 정보 | 외부 근거 우선 | 모델이 내부 지식 고집 |
| 외부 문서가 부정확·모호 | 내부 지식 또는 불확실성 표현 | 외부 문서 맹신 |
| 둘 다 불확실 | abstention / 한계 명시 | 확신 있는 오답 |

따라서 **단순 retrieval 성능**뿐 아니라, 충돌 상황에서 **어떤 근거를 우선할지** 학습·평가하는 것이 중요하다. PA-RAG는 informativeness·robustness·citation을 다루지만, 위 **knowledge conflict**를 명시적 정렬 축으로 다루지 않는다 — 본 연구의 확장 지점.

<br/>

## 방법론 개요 (비교군)

아래 다섯 arm을 동일한 retrieval·질문 설정에서 비교하는 것을 목표로 한다 (`docs/experiment_design.md`).

| # | Arm | 학습 | 역할 |
|---|-----|:----:|------|
| 1 | **Base RAG** | 없음 | 기본 RAG 하한선 |
| 2 | **Conflict-aware prompting** | 없음 | 프롬프트만으로 충돌 처리 |
| 3 | **PA-RAG-style LoRA** | DPO + LoRA | conflict 없이 PA-RAG식 정렬 |
| 4 | **Conflict-Aware RAG LoRA** | DPO + LoRA | conflict preference만 학습 |
| 5 | **Conflict-Aware PA-RAG LoRA** | DPO + LoRA | PA-RAG 단계 + conflict (**제안 방법**) |

설정 파일: `configs/` · 프롬프트: `prompts/` · 데이터 스키마: `data/schema/`

> **Full FT reference:** 자원 한계로 PA-RAG 원문의 full fine-tuning은 재현하지 않고, 필요 시 논문 수치를 **인용 비교**로만 활용.

<br/>

## 🧭 프로젝트 개요

RAG generator를 preference optimization으로 정렬하는 **PA-RAG**를 base로 삼고, **DPO + LoRA**로 학부 수준 자원에서 실험 가능성을 확보. Conflict resolution을 **prompting/후처리**에 둘지 **preference learning으로 내재화**할지, 내재화한다면 **어디까지 가능한지**를 탐구.

<br/>

## 💡 핵심 연구 질문 (RQ)

1. Preference learning으로 conflict resolution을 **내재화**할 수 있는가?
2. 어떤 conflict pattern은 학습되고 어떤 것은 한계인가?
3. **Prompting** 대비 **LoRA 내재화**는 얼마나 효과적인가? (프로토콜 확정 후 측정)
4. Conflict 정렬이 informativeness 등 다른 축을 해치지 않는가?

<br/>

## 🔬 PA-RAG와의 관계

```mermaid
flowchart LR
    subgraph PA["PA-RAG (Base)"]
        A[Informativeness]
        B[Robustness]
        C[Citation Quality]
    end
    subgraph OURS["본 연구 (확장)"]
        D[Knowledge Conflict ← context–memory]
    end
    PA --> OURS
    style D fill:#ff6b6b,color:#fff
```

| 기준 | PA-RAG | 본 연구 |
|---|---|:---:|
| Informativeness | ✅ | ✅ (비교·확장) |
| Robustness | ✅ | ✅ |
| Citation Quality | ✅ | ✅ |
| **Knowledge Conflict (context–memory)** | ❌ | ✅ |

<br/>

## 📚 문서 및 벤치마크 (초안)

| 문서 | 내용 |
|------|------|
| `docs/research_plan.md` | 문제 정의, RQ, 기여, 한계 |
| `docs/related_work.md` | 관련 논문 citation placeholder |
| `docs/benchmark_selection.md` | ClashEval, ConflictBank 등 후보 (**final decision pending**) |
| `docs/experiment_design.md` | 비교군 상세 |
| `docs/decision_log.md` | 확정·보류·제외 결정 |
| `docs/submission_materials/` | 기존 `doc/` 자료 보존 (수업 제출, PA-RAG 독서 노트 등) |

벤치마크·데이터셋 전략 요약(확정 전): ClashEval·ConflictBank(학습 후보), WikiContradict(평가·자연 conflict), CONFLICTS/DRAGged(스키마 참고) — 상세는 `docs/benchmark_selection.md`.

<br/>

## 🛠 기술 스택 (계획)

### AI / 학습

| 역할 | 기술 |
|------|------|
| Preference Learning | DPO (TRL) |
| 경량 Fine-tuning | LoRA / PEFT |
| 런타임 | PyTorch, Hugging Face `transformers` |

### RAG / 검색

| 역할 | 기술 | 비고 |
|------|------|------|
| Baseline local vector store | **FAISS** or **Chroma** | 스캐폴드 단계 후보; `requirements.txt`에 FAISS만 명시 |
| Scalable retrieval backend (후보) | **OpenSearch** | 대규모·분산 검색 후보 — **미확정**, 의존성 주석 처리 |

### 평가

| 역할 | 기술 | 비고 |
|------|------|------|
| 자동 평가 | RAGAS 등 | 프로토콜 **TBD** |
| 정성 평가 | LLM-as-a-judge (`prompts/judge_prompt.md`) | 루브릭 초안만 존재 |

의존성 목록: `requirements.txt` (스캐폴드에 필요한 최소 패키지; 미사용 무거운 패키지는 TODO 주석).

<br/>

## ▶️ 실행 (Placeholder)

| 모듈 | 실행 | 비고 |
|:--:|:--|:--|
| **RAG** | `python rag/pipeline_stub.py` | 인터페이스만 |
| **Fine-tuning** | `python finetuning/train_stub.py` | 인터페이스만 |
| **Eval** | `python eval/evaluate_stub.py` | 인터페이스만 |
| **데모** | `self_demo.md` | to be updated |

<br/>

## 📁 저장소 구조

```text
Graduation-Project/
├── configs/           # 실험군별 YAML (값 TBD / null)
├── data/
│   ├── schema/        # conflict·preference JSON Schema + fictitious example
│   ├── synthetic/     # DPO 학습용 synthetic conflict (planned)
│   └── natural/       # natural conflict case study (planned)
├── docs/              # 연구 계획·벤치마크·실험 설계·결정 로그
│   └── submission_materials/  # 구 doc/ 보존 자료
├── eval/              # 평가 스크립트 (stub)
├── finetuning/        # DPO + LoRA (stub; dpo/, lora/)
├── prompts/           # RAG·conflict-aware·judge 프롬프트 초안
├── rag/               # Base RAG 파이프라인 (stub)
├── results/           # 실험 산출물 (아직 없음)
├── .env.example
├── self_demo.md       # 발표용 데모 placeholder
├── CLAUDE.md
├── index.html         # GitHub Pages
├── README.md
└── requirements.txt
```

### 처음 보는 사람을 위한 읽는 순서

1. 본 README **저장소 상태**와 `docs/decision_log.md`
2. `docs/research_plan.md`, `docs/experiment_design.md`
3. `data/schema/`, `prompts/`, `configs/`
4. `rag/pipeline_stub.py`, `finetuning/train_stub.py`, `eval/evaluate_stub.py` (진입점 형태만)
5. 벤치마크 확정 후 `data/`, `eval/`, `results/` 채움

<br/>

## 🌿 브랜치 전략

```
main ← 최종 제출 / 논문 기준
 └── dev ← 통합 개발 (PR 타겟)
      ├── feat/data/#이슈번호-설명
      ├── feat/dpo/#이슈번호-설명
      ├── feat/rag/#이슈번호-설명
      ├── feat/eval/#이슈번호-설명
      └── fix/#이슈번호-설명
```

<br/>

## 👥 팀

**팀명:** Alltology · **트랙:** 연구 · **지도교수:** 황의원 교수님

| <img src="https://github.com/ryeong03.png" width="120" /> | <img src="https://github.com/bbberylll.png" width="120" /> | <img src="https://github.com/dev-ldy03.png" width="120" /> |
|:--:|:--:|:--:|
| **박세령** | **손현경** | **이다영** |
| Conflict type 설계 · RAG 파이프라인 | DPO 학습 · LoRA fine-tuning | 데이터 파이프라인 · 평가 |
| [@ryeong03](https://github.com/ryeong03) | [@bbberylll](https://github.com/bbberylll) | [@dev-ldy03](https://github.com/dev-ldy03) |

<br/>

<div align="center">
<sub>이화여자대학교 졸업프로젝트 2026</sub>
</div>
