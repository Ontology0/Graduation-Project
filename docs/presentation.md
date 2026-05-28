---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    font-size: 24px;
    font-weight: 500;
    background: #F6EBDB;
    color: #3a2e2e;
    padding: 130px 60px 50px 60px;
    box-sizing: border-box;
    position: relative;
  }
  section.title {
    background: linear-gradient(135deg, #AC9799 0%, #CF726F 60%, #E99B84 100%);
    color: white;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  section.title h1 { font-size: 40px; font-weight: 800; color: white; margin-bottom: 12px; line-height: 1.3; }
  section.title h2 { font-size: 22px; font-weight: 500; color: #F9EEEB; }
  section.title p  { font-size: 17px; color: #F6EBDB; margin-top: 40px; line-height: 1.8; }
  section.title a  { color: #F9EEEB; }
  section:not(.title) h1 { position: absolute; top: 44px; left: 0; right: 0; padding: 0 60px 12px 60px; font-size: 32px; font-weight: 800; color: #CF726F; border-bottom: 3px solid #CF726F; margin: 0; }
  h2 { font-size: 26px; font-weight: 700; color: #AC9799; margin-bottom: 14px; }
  p { line-height: 1.7; }
  ul, ol { padding-left: 1.4em; line-height: 1.8; }
  table { width: 100%; border-collapse: collapse; font-size: 19px; }
  th { background: #CF726F; color: white; padding: 10px 14px; font-weight: 700; }
  td { padding: 9px 14px; border: 1px solid #DBD0C3; }
  tr:nth-child(even) { background: #F9EEEB; }
  .highlight { background: #F9EEEB; border-left: 5px solid #E99B84; padding: 10px 16px; border-radius: 4px; margin: 8px 0; }
  .green { color: #6b8f6b; font-weight: bold; }
  .red { color: #CF726F; font-weight: bold; }
  .blue { background: #F9EEEB; border-left: 5px solid #AC9799; padding: 10px 16px; border-radius: 4px; margin: 8px 0; }
  code { background: #DBD0C3; border-radius: 3px; padding: 1px 5px; font-size: 90%; }
  pre { background: #DBD0C3; border-radius: 6px; font-size: 17px; width: 100%; }
  pre code { background: none; padding: 0; }
  blockquote { border-left: 5px solid #E99B84; color: #7a5c5c; background: #F9EEEB; padding: 8px 16px; margin: 8px 0; border-radius: 0 4px 4px 0; }
  section.qa { font-size: 20px; }
  section.qa h1 { font-size: 28px; }
  section.qa blockquote { font-size: 18px; }
---

<!-- _class: title -->

# RAG에서 지식 충돌 완화를 위한<br/>Preference Learning 기반 정렬 연구

## Conflict-Aware PA-RAG

<p>
팀 03 · Alltology<br/>
이화여자대학교 캡스톤디자인 2026 · 지도교수: 황의원 교수님<br/><br/>
박세령 (2276121) · 손현경 (2329019) · 이다영 (2317022)
</p>

---

# 목차

1. **문제 포착** — 왜 이 문제인가?
2. **연구 배경 · 가치** — PA-RAG가 다루지 않은 것
3. **관련 연구** — 기존 접근과 한계
4. **제안 솔루션** — Conflict-Aware PA-RAG
5. **기술 아키텍처 · MVP**
6. **라이브 데모**
7. **AI 투명성 리포트**
8. **Q&A**

---

# 팀 소개

| | 박세령 (2276121) | 손현경 (2329019) | 이다영 (2317022) |
|:---:|:---:|:---:|:---:|
| **역할** | Conflict type 설계<br/>RAG 파이프라인 구현 | DPO 학습 설계<br/>LoRA fine-tuning | 데이터 파이프라인<br/>평가 프로토콜 |
| **GitHub** | @ryeong03 | @bbberylll | @dev-ldy03 |

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

# 2. 연구 배경 · 가치

## PA-RAG가 다루지 않은 것

PA-RAG (NAACL 2025)는 RAG generator를 세 기준으로 정렬한다:

> **① Informativeness · ② Robustness · ③ Citation Quality**

그러나 **Knowledge Conflict — 검색 문서와 내부 지식이 충돌하는 상황** 은 명시적 정렬 축에 없다.

<br/>

| 충돌 상황 | 이상적 행동 | PA-RAG의 한계 |
|-----------|------------|--------------|
| 외부 문서가 최신·권위 정보 | 외부 우선 | 정렬 기준 없음 → 불일치 |
| 외부 문서가 부정확 | 내부 지식 또는 abstention | 외부 맹신 가능 |
| 둘 다 불확실 | 불확실성 표현 | 확신 있는 오답 |

<br/>

<div class="highlight">
<b>연구 질문:</b> PA-RAG 프레임워크에 <b>Knowledge Conflict 해소</b>를 4번째 정렬 기준으로 추가하면,<br/>
prompting 없이도 모델이 충돌을 올바르게 판단할 수 있는가?
</div>

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

# 4. 제안 솔루션 — 독창성

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

![w:580 center](https://raw.githubusercontent.com/Ontology0/Graduation-Project/refactoring/docs/assets/rag_diagram.png)

**구현:** `src/rag/` (10개 모듈) · FAISS 벡터스토어 · sentence-transformers 임베딩

---

# 5. 기술 아키텍처 — MVP 현황

| 컴포넌트 | 상태 | 비고 |
|----------|------|------|
| Base RAG 파이프라인 | ✅ 구현 완료 | `src/rag/` 10개 모듈 |
| Conflict-Aware Prompting | ✅ 구현 완료 | `configs/prompts/` |
| 실험 비교 데모 (HF Spaces) | ✅ 배포 완료 | 실시간 Base vs CA 비교 |
| 저장소 문서 RAG 챗봇 (Telegram) | ✅ 배포 완료 | @alltology_rag_bot |
| DPO + LoRA 학습 | 🔧 Scaffold | `src/training/` |
| 벤치마크 평가 파이프라인 | 🔧 Scaffold | `src/evaluation/` |

<br/>

> DPO 학습 · 벤치마크 평가 파이프라인 구현 진행 중

---

# 6. 라이브 데모 ① — 실험 비교

![bg right:48%](https://raw.githubusercontent.com/Ontology0/Graduation-Project/refactoring/docs/assets/demo_screenshot.png)

**HuggingFace Spaces**
[ponyo03/conflict-aware-rag-demo](https://huggingface.co/spaces/ponyo03/conflict-aware-rag-demo)

<br/>

- Base RAG vs Conflict-Aware **실시간 비교**
- 샘플 질문으로 바로 테스트 가능
- 검색 문서 수(Top-K) 조정 가능

<br/>

> "What color is the Northwood Institute mascot after the 2019 revision?"
> Base → deep blue / Conflict-Aware → silver-green

---

# 6. 라이브 데모 ② — RAG 챗봇

![bg right:36% fit](https://raw.githubusercontent.com/Ontology0/Graduation-Project/refactoring/docs/assets/bot_screenshot.png)

**Telegram Bot**
[@alltology_rag_bot](https://t.me/alltology_rag_bot)

<br/>

- README · docs · CLAUDE.md를 청킹·임베딩
- 벡터 검색으로 관련 문맥 삽입 → LLM 답변 생성
- 저장소 내용 기반 Q&A 자동화

---

# 6. 라이브 데모 ③ — 연구 사이트

![bg right:50%](https://raw.githubusercontent.com/Ontology0/Graduation-Project/refactoring/docs/assets/web_screenshot.png)

**alltology.zapto.org**
[alltology.zapto.org](http://alltology.zapto.org)

<br/>

- 연구 배경 · 핵심 연구 질문 공개
- 실험 설계 · 관련 연구 정리

---

# 6. 라이브 데모 ④ — 데모 · 팀

![bg right:52%](https://raw.githubusercontent.com/Ontology0/Graduation-Project/refactoring/docs/assets/web_screenshot2.png)

**직접 해보기**

- 🚀 웹 데모 · 텔레그램 봇 바로가기
- 팀원 소개 (박세령 · 손현경 · 이다영)
- GitHub 저장소 연동

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

# 8. 결론 및 기대 효과

## 요약

- **문제:** PA-RAG는 Knowledge Conflict를 명시적 정렬 축으로 다루지 않음
- **제안:** DPO + LoRA로 conflict resolution을 **모델에 내재화** (4번째 정렬 기준)
- **현재:** Base RAG + Conflict-Aware Prompting 구현 완료, 라이브 데모 배포 — DPO 학습 · 평가 진행 중

## 기대 효과

| 기여 | 내용 |
|------|------|
| 학술적 | PA-RAG 확장 — conflict resolution을 preference learning으로 내재화하는 첫 시도 |
| 실용적 | 경량 (LoRA) 접근으로 학부 수준 자원에서 재현 가능한 파이프라인 공개 |
| 한계 분석 | synthetic 학습이 natural conflict에 얼마나 전이되는지 측정 |

---

<!-- _class: qa -->

# 9. Q&A — 예상 질문 (1/2)

**Q1. Prompting으로도 충분하지 않나요? 왜 굳이 학습인가요?**
> Prompting은 매 추론마다 명시적 지시가 필요하고, 프롬프트 설계에 따라 일관성이 달라집니다. DPO로 내재화하면 별도 지시 없이도 일관된 판단이 가능하다는 것을 실증하는 것이 본 연구의 핵심입니다.

<br/>

**Q2. DPO 학습 데이터는 어떻게 구성하나요?**
> ClashEval · ConflictBank의 conflict 쌍에서 chosen(올바른 판단) / rejected(잘못된 판단) 쌍을 구성합니다. 외부 문서가 권위 있을 때는 외부 우선, 오래됐거나 부정확할 때는 내부 우선 등 resolution rule을 레이블로 사용합니다.

---

<!-- _class: qa -->

# 9. Q&A — 예상 질문 (2/2)

**Q3. 학습 후 다른 정렬 기준(informativeness 등)이 나빠지지 않나요?**
> PA-RAG의 기존 세 기준에 conflict 기준을 추가하는 구조라, 기존 정렬과 충돌하는지가 핵심 연구 질문(RQ4)입니다. 이 트레이드오프를 실험으로 측정하는 것이 본 연구의 중요한 기여 중 하나입니다.

<br/>

**Q4. 평가는 어떻게 진행하나요?**
> ClashEval · WikiContradict 벤치마크 기반 정량 평가와 Northwood 같은 케이스 스터디 정성 분석을 병행합니다. conflict resolution 정확도, 기존 정렬 기준 유지 여부(trade-off)를 핵심 지표로 측정합니다.

---

<!-- _class: title -->

# 감사합니다

<p>
GitHub: <a href="https://github.com/Ontology0/Graduation-Project" style="color:#F9EEEB">github.com/Ontology0/Graduation-Project</a><br/>
데모 사이트: <a href="http://alltology.zapto.org" style="color:#F9EEEB">alltology.zapto.org</a><br/>
<br/>
팀 03 · Alltology · 박세령 (2276121) · 손현경 (2329019) · 이다영 (2317022)
</p>
