---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    font-size: 22px;
  }
  section.title {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    text-align: center;
  }
  section.title h1 { font-size: 36px; color: white; margin-bottom: 8px; }
  section.title h2 { font-size: 20px; color: #a8d8ea; font-weight: normal; }
  section.title p  { font-size: 16px; color: #cccccc; margin-top: 40px; }
  h1 { font-size: 30px; color: #0f3460; border-bottom: 3px solid #0f3460; padding-bottom: 8px; }
  h2 { font-size: 24px; color: #16213e; }
  table { width: 100%; border-collapse: collapse; font-size: 18px; }
  th { background: #0f3460; color: white; padding: 8px 12px; }
  td { padding: 7px 12px; border: 1px solid #ddd; }
  tr:nth-child(even) { background: #f4f8ff; }
  .highlight { background: #fff3cd; border-left: 4px solid #ffc107; padding: 8px 14px; border-radius: 4px; }
  .green { color: #2d6a4f; font-weight: bold; }
  .red { color: #c0392b; font-weight: bold; }
  .blue { background: #e8f4fd; border-left: 4px solid #2980b9; padding: 8px 14px; border-radius: 4px; }
---

<!-- _class: title -->

# RAG에서 지식 충돌 완화를 위한<br/>Preference Learning 기반 정렬 연구

## Conflict-Aware PA-RAG

<p>
팀 03 · Alltology<br/>
박세령 · 손현경 · 이다영<br/>
지도교수: 황의원 교수님<br/>
이화여자대학교 캡스톤디자인 2026
</p>

---

# 목차

1. **문제 포착** — 왜 이 문제인가?
2. **문제 정의** — 무엇을 해결하는가?
3. **관련 연구** — 기존 접근과 한계
4. **제안 솔루션** — Conflict-Aware PA-RAG
5. **기술 아키텍처 · MVP**
6. **라이브 데모**
7. **AI 투명성 리포트**

---

# 1. 문제 포착

## RAG가 있어도 틀리는 경우가 있다

> "Northwood Institute의 마스코트 색상은?"

| | 모델 내부 지식 (Parametric) | 검색된 외부 문서 (Retrieved) |
|---|---|---|
| 답변 | **deep blue** | **silver-green** (2019 개정판) |
| 근거 | 학습 당시 기억 | 실제 검색 결과 |

<br/>

<div class="highlight">
RAG 시스템이 외부 문서를 제공해도, 모델은 <b>내부 지식을 고집</b>하거나 <b>맹목적으로 문서를 따를 수</b> 있다.
</div>

---

# 2. 문제 정의

## Context–Memory Conflict

| 충돌 상황 | 바람직한 행동 | 현재 문제 |
|-----------|--------------|-----------|
| 외부 문서가 최신·권위 정보 | 외부 근거 우선 | 모델이 내부 지식 고집 |
| 외부 문서가 부정확·오래된 정보 | 내부 지식 또는 불확실성 표현 | 외부 문서 맹신 |
| 둘 다 불확실 | Abstention / 한계 명시 | 확신 있는 오답 |

<br/>

**고객:** RAG 시스템을 실제로 사용하는 조직·연구자 (도메인 지식 정확성이 중요한 상황)

**가치 제안:** 충돌 상황에서 어떤 근거를 따를지 **별도 post-processing 없이** 모델 내부에 내재화

---

# 3. 관련 연구

## 기존 접근의 한계

| 연구 | 방법 | 한계 |
|------|------|------|
| **PA-RAG** (NAACL 2025) | DPO로 정보성·강건성·인용 품질 정렬 | Knowledge Conflict를 명시적 기준으로 다루지 않음 |
| **ClashEval** (2024) | 내부 vs. 외부 충돌 현상 측정 | 해결 방법론 없음 |
| **ConflictBank** (2024) | 충돌 유형 분류 벤치마크 | 학습 기반 해결 없음 |
| **Prompting 접근** | 프롬프트로 외부 우선 지시 | 학습 없음, 일관성 한계 |

<br/>

<div class="blue">
<b>공통 한계:</b> 충돌 해소를 외부 모듈(prompting·후처리)에 의존 — 모델 자체가 판단 기준을 갖지 못함
</div>

---

# 4. 제안 솔루션

## Conflict-Aware PA-RAG

PA-RAG의 정렬 기준 3가지에 **Knowledge Conflict 해소**를 4번째 기준으로 추가

```
PA-RAG (기존)         →   Conflict-Aware PA-RAG (제안)
──────────────────────    ──────────────────────────────────
① Informativeness         ① Informativeness
② Robustness              ② Robustness
③ Citation Quality        ③ Citation Quality
                      +   ④ Conflict Resolution  ← 신규
```

<br/>

**학습 방식:** DPO + LoRA (full fine-tuning 대신 경량화 → 학부 수준 자원에서 재현 가능)

**데이터:** ClashEval · ConflictBank (synthetic) → WikiContradict (natural, 한계 분석용)

---

# 4-1. 독창성 · 차별성

| | 기존 RAG | Prompting 기반 | **본 연구 (제안)** |
|---|---|---|---|
| 충돌 감지 | ❌ | ⚠️ 프롬프트 의존 | ✅ 학습으로 내재화 |
| 일관성 | ❌ | ⚠️ 프롬프트마다 다름 | ✅ 모델 내부 정렬 |
| 추가 비용 | — | 프롬프트 설계 비용 | LoRA만 추가 학습 |
| 확장성 | ❌ | 제한적 | ✅ 다양한 conflict 유형 |

<br/>

<div class="highlight">
<b>핵심 주장:</b> Prompting으로 외부에서 지시하는 것보다, DPO+LoRA로 <b>모델 내부에 내재화</b>하는 것이 더 일관적이고 강건한 충돌 해소를 가능하게 하는가 — 를 실증한다.
</div>

---

# 5. 기술 아키텍처

```
질문 입력
   │
   ▼
┌─────────────────────────────────────────────┐
│              RAG Pipeline                   │
│  Document → Chunk → Embed → VectorStore     │
│                                ↓            │
│              질문 Embedding → Retrieve       │
│                                ↓            │
│         [retrieved context + question]      │
│                                ↓            │
│    PromptBuilder (Base / Conflict-Aware)    │
│                                ↓            │
│              Generator (LLM)               │
└─────────────────────────────────────────────┘
   │
   ▼
답변 + 출처
```

**구현:** `src/rag/` (10개 모듈) · FAISS 벡터스토어 · sentence-transformers 임베딩

---

# 5-1. MVP 구성 현황

| 컴포넌트 | 상태 | 비고 |
|----------|------|------|
| Base RAG 파이프라인 | ✅ 구현 완료 | `src/rag/` 10개 모듈 |
| Conflict-Aware Prompting | ✅ 구현 완료 | `configs/prompts/` |
| 실험 비교 데모 (HF Spaces) | ✅ 배포 완료 | 실시간 Base vs CA 비교 |
| 저장소 문서 RAG 챗봇 (Telegram) | ✅ 배포 완료 | @alltology_rag_bot |
| DPO + LoRA 학습 | 🔧 Scaffold | `src/training/` |
| 벤치마크 평가 파이프라인 | 🔧 Scaffold | `src/evaluation/` |

<br/>

> 연구 scaffold 단계 — 실험 결과는 추후 업데이트 예정

---

# 6. 라이브 데모

## 지금 직접 확인해보세요

**실험 비교:** [huggingface.co/spaces/ponyo03/conflict-aware-rag-demo](https://huggingface.co/spaces/ponyo03/conflict-aware-rag-demo)

> "What color is the Northwood Institute mascot after the 2019 revision?"
>
> - **Base RAG** → 내부 지식 고집 (deep blue 가능)
> - **Conflict-Aware** → 검색 문서 우선 (silver-green)

<br/>

**저장소 RAG 챗봇:** [@alltology_rag_bot](https://t.me/alltology_rag_bot)

> README · docs · CLAUDE.md를 지식베이스로 청킹·임베딩<br/>
> 벡터 검색 → 관련 문맥 삽입 → 답변 생성

<br/>

**연구 사이트:** [alltology.zapto.org](http://alltology.zapto.org)

---

# 7. AI 투명성 리포트

## AI 활용 내역 (주요)

| 단계 | 사용 도구 | AI 수행 | **인간 판단** |
|------|-----------|---------|--------------|
| 선행 연구 분석 | Claude, NotebookLM | 논문 요약, 방법론 정리 | 원문 대조 검증, 범위 결정 |
| 레포 구조 설계 | Cursor (Claude) | 리팩토링, 파일 이동, import 수정 | 구조 방향 승인, 네이밍 결정 |
| RAG 파이프라인 구현 | Cursor (Claude) | 모듈 코드 생성 | 모듈 분할 방식, 모델 선택 |
| 실험 설계 | GPT-4o | 데이터 스키마 초안 | 충돌 유형 정의, 평가 기준 결정 |

<br/>

<div class="blue">
<b>원칙:</b> AI 출력은 항상 팀이 검토 후 채택 · 수정 · 거부 결정 → 모든 핵심 판단은 인간이 수행
</div>

---

<!-- _class: title -->

# 감사합니다

## Q & A

<p>
GitHub: <a href="https://github.com/Ontology0/Graduation-Project" style="color:#a8d8ea">github.com/Ontology0/Graduation-Project</a><br/>
데모 사이트: <a href="http://alltology.zapto.org" style="color:#a8d8ea">alltology.zapto.org</a><br/>
<br/>
팀 03 · Alltology<br/>
박세령 · 손현경 · 이다영
</p>
