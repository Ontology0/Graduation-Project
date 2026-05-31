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
    padding: 50px 60px;
    box-sizing: border-box;
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
  section:not(.title) { position: relative; }
  section:not(.title) h1 {
    position: absolute;
    top: 50px;
    left: 0;
    right: 0;
    height: 52px;
    line-height: 52px;
    font-size: 30px;
    font-weight: 800;
    color: #CF726F;
    border-bottom: 3px solid #CF726F;
    padding: 0 60px;
    margin: 0;
    box-sizing: border-box;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    z-index: 2;
  }
  section:not(.title) > h2:first-of-type {
    position: absolute;
    top: 120px;
    left: 60px;
    right: 60px;
    margin: 0;
    min-height: 38px;
    line-height: 1.35;
    z-index: 2;
  }
  section:not(.title) > h2:first-of-type + * { margin-top: 112px; }
  section:not(.title) h1 + :not(h2) { margin-top: 112px; }
  section:not(.title) > h2:not(:first-of-type) {
    position: static;
    margin-top: 1.2em;
    margin-bottom: 10px;
  }
  h2 { font-size: 26px; font-weight: 700; color: #AC9799; margin-bottom: 14px; }
  p { line-height: 1.7; margin: 6px 0; }
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
  section.qa h1 { font-size: 28px; line-height: 52px; }
  section.qa blockquote { font-size: 18px; }
  section.team-intro > h2:first-of-type + .team-table-wrap { margin-top: 0 !important; }
  section.team-intro .team-table-wrap {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: max-content;
    max-width: calc(100% - 100px);
    z-index: 1;
  }
  section.team-intro .team-table-wrap table { width: auto; margin: 0; font-size: 22px; }
  section.team-intro th,
  section.team-intro td { text-align: center; vertical-align: middle; padding: 14px 20px; }
  section.arch-center { text-align: center; }
  section.arch-center img { display: block; margin: 0 auto 14px; max-width: 580px; }
  section.mvp-table table { width: 94%; max-width: 920px; margin: 0 auto; font-size: 20px; }
  section.mvp-table th,
  section.mvp-table td { text-align: center; vertical-align: middle; }
  section.contrib table { font-size: 18px; }
  section.contrib th, section.contrib td { padding: 8px 12px; vertical-align: top; }
  section.demo-bot img.bot-img {
    position: absolute;
    right: 60px;
    top: calc(50% + 26px);
    transform: translateY(-50%);
    height: 480px;
    max-width: 42%;
    object-fit: contain;
    z-index: 0;
  }
  section.demo-bot .demo-text { width: 52%; position: relative; z-index: 1; }
  section.demo-web-left img.demo-shot {
    position: absolute;
    right: 60px;
    top: calc(50% + 12px);
    transform: translateY(-50%);
    max-height: 88%;
    max-width: 48%;
    object-fit: contain;
    z-index: 0;
  }
  section.demo-web-left .demo-text { width: 52%; position: relative; z-index: 1; }
  section.toc .toc-cols {
    display: flex;
    gap: 48px;
    margin-top: 112px;
  }
  section.toc .toc-cols > div { flex: 1; }
  section.toc .toc-cols ol, section.toc .toc-cols ul { padding-left: 1.2em; }
  section.toc .toc-cols li { margin-bottom: 10px; line-height: 1.6; }
  section.advisor { font-size: 17px; }
  section.advisor h1 { font-size: 28px; line-height: 52px; }
  section.advisor h2 { font-size: 21px; }
  section.advisor table { font-size: 16px; margin-bottom: 8px; }
  section.advisor ul { font-size: 16px; line-height: 1.55; margin: 4px 0; }
  section.advisor .highlight { font-size: 16px; line-height: 1.55; padding: 8px 14px; }
  section.advisor .sign { text-align: right; margin-top: 10px; font-size: 16px; line-height: 1.6; }
---

<!-- _class: title -->

# RAG에서 지식 충돌 완화를 위한<br/>Preference Learning 기반 정렬 연구

## Conflict-Aware PA-RAG<br/><span style="font-size:18px; font-weight:500;">작은 모델은 어디까지 배울 수 있는가 — LoRA 기반 지식 충돌 정렬의 한계 분석</span>

<p>
팀 03 · Alltology<br/>
이화여자대학교 캡스톤디자인 2026 · 지도교수: 황의원 교수님<br/><br/>
박세령 (2276121) · 손현경 (2329019) · 이다영 (2317022)
</p>

---

<!-- _class: toc -->

# 목차

## 발표 순서

<div class="toc-cols">
<div>

1. **프로젝트 제목과 팀 소개**
2. **문제 정의**
3. **타깃 사용자와 사용 시나리오**
4. **기존 방식의 한계**
5. **솔루션 개요**
6. **시스템 구조도**

</div>
<div>

7. **핵심 기술 및 구현 내용**
8. **Live Demo 시나리오**
9. **구현 결과 및 현재 완성도**
10. **한계와 향후 개선 방향**
11. **팀원별 역할 및 기여**
12. **GitHub / 배포 URL / 참고자료**
13. **AI 투명성 리포트**
14. **Q&A 세션**
15. **지도교수 의견서**

</div>
</div>

---

<!-- _class: team-intro -->

# 1. 프로젝트 · 팀 소개

## Conflict-Aware PA-RAG | Alltology

<div class="team-table-wrap">

| | 박세령 (2276121) | 손현경 (2329019) | 이다영 (2317022) |
|:---:|:---:|:---:|:---:|
| **역할** | Conflict type 설계<br/>RAG 파이프라인 구현 | DPO 학습 설계<br/>연구 설계 · 파일럿 실험 | 데이터 파이프라인<br/>평가 프로토콜 |
| **GitHub** | @ryeong03 | @bbberylll | @dev-ldy03 |

</div>

---

# 2. 문제 정의

## Knowledge Conflict — 검색 문서 vs 내부 지식

> "Northwood Institute의 마스코트 색상은?" (2019년 개정)

| | 모델 내부 지식 (Parametric) | 검색된 외부 문서 (Retrieved) |
|---|---|---|
| 답변 | **deep blue** | **silver-green** ✅ |
| 근거 | 학습 당시 기억 | 실제 최신 문서 |

<br/>

| 충돌 상황 | 이상적 행동 | 실제 문제 |
|---|---|---|
| 외부 문서가 최신·권위 정보 | 외부 우선 | 내부 지식 고집 |
| 외부 문서가 부정확 | 내부 지식 또는 abstention | 외부 맹신 |
| 둘 다 불확실 | 불확실성 표현 | 확신 있는 오답 |

---

# 3. 타깃 사용자와 사용 시나리오

## 누가, 어떤 상황에서?

| 타깃 | 문제 상황 |
|------|-----------|
| **NLP/RAG 연구자** | Prompting vs LoRA 내재화 — 충돌 해소 방법론 비교 연구 |
| **RAG 시스템 개발자 · 기업** | 사내 최신 문서가 모델의 기존 지식과 충돌하는 프로덕션 환경 |
| **학부 연구자** | DPO + LoRA 경량 파이프라인을 제한된 자원으로 재현하려는 연구자 |

## 사용 시나리오

<div class="highlight">
① <b>기업 정책 봇:</b> "2024년 개정 육아휴직 규정" 문서 vs 모델 기존 기억 충돌 → 최신 규정으로 정확히 답변<br/>
② <b>의료 가이드라인 QA:</b> 개정 임상 지침 vs 학습 당시 구 지침 충돌 → 외부 근거 우선<br/>
③ <b>학술 QA:</b> 논문 내용과 모델이 아는 "상식"이 다를 때 → 논문 우선 또는 불확실성 표현
</div>

---

# 4. 기존 방식의 한계

## PA-RAG · Prompting · 벤치마크

| 연구 / 접근 | 방법 | **한계** |
|------------|------|---------|
| **PA-RAG** (NAACL 2025) | DPO로 Informativeness · Robustness · Citation 정렬 | Knowledge Conflict를 명시적 정렬 기준으로 다루지 않음 |
| **Prompting 접근** | 외부 우선 지시를 프롬프트에 삽입 | 매 추론마다 명시 필요, 일관성 불안정 |
| **ClashEval** (2024) | 내부 vs. 외부 충돌 현상 측정 | 해결 방법론 없음 — 현상 측정만 |
| **ConflictBank** (2024) | 충돌 유형 분류 벤치마크 | 학습 기반 해결 없음 |

<br/>

<div class="blue">
<b>공통 한계:</b> 충돌 해소를 외부 모듈(prompting · 후처리)에 의존 —<br/>모델 자체가 판단 기준을 갖지 못함
</div>

---

# 5. 솔루션 개요 ①

## Conflict-Aware PA-RAG

PA-RAG의 정렬 기준 3가지에 **Knowledge Conflict 해소**를 4번째 기준으로 추가

```
PA-RAG (기존)              →   Conflict-Aware PA-RAG (제안)
──────────────────────────     ──────────────────────────────────
① Informativeness              ① Informativeness
② Robustness                   ② Robustness
③ Citation Quality             ③ Citation Quality
                           +   ④ Conflict Resolution  ← 신규
```

<br/>

**학습 방식:** DPO + LoRA · 학부 수준 자원에서 재현 가능 (full fine-tuning 미사용)

**데이터:** ClashEval · ConflictBank (synthetic) → WikiContradict (natural, 전이 분석)

---

# 5. 솔루션 개요 ②

## 독창성 · 5-Arm 실험 설계

| # | Arm | 학습 | 역할 |
|---|-----|:----:|------|
| 1 | **Base RAG** | 없음 | 기본 하한선 |
| 2 | **Conflict-Aware Prompting** | 없음 | 프롬프트만으로 충돌 처리 |
| 3 | **PA-RAG-style LoRA** | DPO+LoRA | conflict 없이 PA-RAG식 정렬 |
| 4 | **Conflict-Aware RAG LoRA** | DPO+LoRA | conflict preference만 학습 |
| 5 | **Conflict-Aware PA-RAG LoRA** | DPO+LoRA | PA-RAG + conflict (**제안**) |

<br/>

<div class="highlight">
<b>핵심 질문:</b> Arm 2 (prompting) vs Arm 5 (LoRA 내재화) — 어느 쪽이 더 일관적이고 강건한 충돌 해소를 하는가?
</div>

---

<!-- _class: arch-center -->

# 6. 시스템 구조도

![w:580 center](assets/rag_diagram.png)

**구현:** `src/rag/` (10개 모듈) · FAISS 벡터스토어 · sentence-transformers 임베딩

---

# 7. 핵심 기술 및 구현 내용

## AI / 학습

| 역할 | 기술 |
|------|------|
| Preference Learning | DPO (TRL) |
| 경량 Fine-tuning | LoRA / PEFT |
| 런타임 | PyTorch · Hugging Face `transformers` |

## RAG 파이프라인 — `src/rag/` (10개 모듈)

| 모듈 그룹 | 구성 |
|-----------|------|
| 문서 처리 | `document_loader` · `chunker` |
| 검색 | `embedder` (MiniLM) · `vector_store` (FAISS) · `retriever` |
| 생성 | `prompt_builder` · `generator` · `pipeline` (오케스트레이터) |

---

# 8. Live Demo 시나리오 ①

## 데모 영상

**[▶ youtu.be/qc0GkgJoBBk](https://youtu.be/qc0GkgJoBBk)**

<br/>

## HuggingFace Spaces — Base vs Conflict-Aware 실시간 비교

**[ponyo03/conflict-aware-rag-demo](https://huggingface.co/spaces/ponyo03/conflict-aware-rag-demo)**

> "What color is the Northwood Institute mascot after the 2019 revision?"
> Base RAG → **deep blue** / Conflict-Aware → **silver-green** ✅

- Top-K 검색 수 조정 · 샘플 질문으로 바로 테스트 가능

---

<!-- _class: demo-bot -->

# 8. Live Demo 시나리오 ②

<div class="demo-text">

## Telegram RAG 봇

**[@alltology_rag_bot](https://t.me/alltology_rag_bot)**

<br/>

- README · docs · CLAUDE.md를 청킹·임베딩
- 벡터 검색 → 문맥 삽입 → LLM 답변 생성
- `/about` · `/run` · `/where <키워드>` 지원

</div>

<img class="bot-img" src="assets/bot_screenshot.png" />

---

<!-- _class: demo-web-left -->

# 8. Live Demo 시나리오 ③

<div class="demo-text">

## 연구 사이트

**[alltology.zapto.org](http://alltology.zapto.org)**

<br/>

- 연구 배경 · 핵심 연구 질문 공개
- 실험 설계 · 관련 연구 정리
- HuggingFace · Telegram 버튼 연동

</div>

<img class="demo-shot" src="assets/web_screenshot.png" />

---

<!-- _class: mvp-table -->

# 9. 구현 결과 및 현재 완성도

| 컴포넌트 | 상태 | 비고 |
|----------|------|------|
| Base RAG 파이프라인 | ✅ 완료 | `src/rag/` 10개 모듈 |
| Conflict-Aware Prompting | ✅ 완료 | `configs/prompts/` |
| HuggingFace Spaces 데모 | ✅ 배포 완료 | Base vs CA 실시간 비교 |
| Telegram RAG 봇 | ✅ 배포 완료 | @alltology_rag_bot |
| 연구 사이트 | ✅ 운영 중 | alltology.zapto.org |
| 데모 영상 | ✅ 공개 | youtu.be/qc0GkgJoBBk |
| DPO + LoRA 학습 | 🔧 Scaffold | `src/training/` |
| 벤치마크 평가 파이프라인 | 🔧 Scaffold | `src/evaluation/` |

---

---

<!-- _class: mvp-table -->

# 9-1. 파일럿 실험 결과

## 모델 규모별 충돌 해소 능력 — upper / lower bound 매핑

| 실험 | 셋업 | 핵심 결과 |
|---|---|---|
| **exp1** ClashEval 기본 | 거짓 문서 판별 | Base 50% → Conflict-Aware **100%** (거짓 문서 거부율) |
| **exp2** A/B/C 타입 분해 | 문서 구성 3종 분리 | A(거짓만) Base 50% vs CA **83%** · B·C는 둘 다 100% |
| **exp3** temporal (명시적) | 내부 옛 지식 vs 외부 최신 ("2023년 변경") | 두 arm 모두 update **100%** — 문서가 친절해 추론 불필요 |
| **exp4** temporal (암묵적) | 변화 설명 없이 최신 사실만 전제 | 두 arm 모두 **100%** — 강한 모델 천장효과 |

<div class="highlight">
<b>결론:</b> 강한 모델 = <b>upper bound</b>(충돌 거의 자동 해결) · 약한 모델(phi-2) = <b>lower bound</b>(exp1 실패)<br/>
<b>→ 핵심 질문: 작은 모델(Llama 3.1-8B)을 LoRA/DPO로 upper bound까지 끌어올릴 수 있는가?</b>
</div>

---

# 10. 한계와 향후 개선 방향

## 현재 한계

<div class="highlight">

- DPO 학습 미완 → 정량적 실험 결과 미공개 (파이프라인·설계 단계 완료)
- Synthetic 데이터 학습 시 Natural conflict 전이 성능 불확실
- 자원 한계로 full fine-tuning 미구현 (LoRA 경량화로 대체)
- 벤치마크 자동 평가 파이프라인 미완료

</div>

## 향후 개선 방향

| 단계 | 계획 |
|------|------|
| **단기** | DPO 학습 완료 · ClashEval 벤치마크 정량 평가 실행 |
| **중기** | WikiContradict 자연 충돌 실험 — synthetic → natural 전이 측정 |
| **장기** | 특정 도메인(의료·생활검색 등)에서 강건하게 작동하는 conflict-aware 모델 구축 (general → domain 확장) |

---

<!-- _class: contrib -->

# 11. 팀원별 역할 및 기여

| | 박세령 | 손현경 | 이다영 |
|:---:|:---:|:---:|:---:|
| **주요 담당** | Conflict type 설계<br/>RAG 파이프라인 | DPO 학습 설계<br/>LoRA fine-tuning | 데이터 파이프라인<br/>평가 프로토콜 |
| **주요 기여** | `src/rag/` 10개 모듈 구현<br/>레포 구조·문서화 총괄<br/>연구 사이트 운영 | RQ 구체화·검증, 파일럿 실험 설계·진행·검증<br/>HF Spaces 배포 · DPO scaffold 구현<br/>Conflict preference 데이터 설계 | `data/schema/` 설계<br/>벤치마크 선정 전략<br/>평가 루브릭 설계 |
| **GitHub** | @ryeong03 | @bbberylll | @dev-ldy03 |

<br/>

<div class="blue">
<b>공통:</b> 연구 방향 설계 · AI 출력 교차 검증 · 핵심 로직 판단 — 전원 참여
</div>

---

# 12. GitHub / 배포 URL / 참고자료

## 배포 링크

| 서비스 | URL |
|--------|-----|
| **GitHub 저장소** | github.com/Ontology0/Graduation-Project |
| **연구 사이트** | alltology.zapto.org |
| **HF Spaces 데모** | huggingface.co/spaces/ponyo03/conflict-aware-rag-demo |
| **Telegram RAG 봇** | @alltology_rag_bot |
| **데모 영상** | youtu.be/qc0GkgJoBBk |
| **발표 슬라이드** | github.com/Ontology0/Graduation-Project/blob/dev/docs/presentation.md |

## 참고 논문

| 논문 | 출처 |
|------|------|
| PA-RAG: Preference Alignment for RAG | NAACL 2025 |
| ClashEval: Benchmarking LLM Dilemma | arXiv 2024 |
| ConflictBank: Knowledge Conflicts | arXiv 2024 |

---

# 13. AI 투명성 리포트

## AI 활용 내역 (주요)

| 단계 | 사용 도구 | AI 수행 | **인간 판단** |
|------|-----------|---------|--------------|
| 선행 연구 분석 | Claude, NotebookLM | 논문 요약, 방법론 정리 | 원문 대조 검증, 범위 결정 |
| 레포 구조 설계 | Cursor (Claude) | 리팩토링, 파일 이동, import 수정 | 구조 방향 승인, 네이밍 결정 |
| RAG 파이프라인 구현 | Cursor (Claude) | 모듈 코드 생성 | 모듈 분할 방식, 모델 선택 |
| Telegram RAG 봇 | Cursor (GPT-5) | UX·보안·운영 문서화 | 공개 범위, allowlist 정책 확정 |
| 파일럿 실험 | Claude(haiku/sonnet) · gpt-4o-mini | 데이터 스키마 초안, 실험 코드 보조 | 충돌 유형 정의, 평가 기준 결정, 결과 해석 |

<br/>

> 상세: [docs/ai_transparency_report.md](docs/ai_transparency_report.md)

---

<!-- _class: qa -->

# 14. Q&A 세션 ①

**Q1. Prompting으로도 충분하지 않나요? 왜 굳이 학습인가요?**
> Prompting은 매 추론마다 명시적 지시가 필요하고, 프롬프트 설계에 따라 일관성이 달라집니다. DPO로 내재화하면 별도 지시 없이도 일관된 판단이 가능하다는 것을 실증하는 것이 핵심입니다.

<br/>

**Q2. DPO 학습 데이터는 어떻게 구성하나요?**
> ClashEval · ConflictBank의 conflict 쌍에서 chosen(올바른 판단) / rejected(잘못된 판단) 쌍을 구성합니다. 외부 문서가 권위 있을 때는 외부 우선, 부정확할 때는 내부 우선 등 resolution rule을 레이블로 사용합니다.

---

<!-- _class: qa -->

# 14. Q&A 세션 ②

**Q3. 학습 후 informativeness 등 기존 기준이 나빠지지 않나요?**
> 이 트레이드오프가 핵심 RQ4입니다. PA-RAG 기존 세 기준 + conflict 기준을 함께 실험하면서 trade-off를 측정하는 것이 중요한 기여입니다.

<br/>

**Q4. 평가는 어떻게 진행하나요?**
> ClashEval · WikiContradict 벤치마크 기반 정량 평가와 케이스 스터디 정성 분석을 병행합니다. Conflict resolution 정확도, 기존 정렬 기준 유지 여부(trade-off)를 핵심 지표로 측정합니다.

---

<!-- _class: advisor -->

# 15. 지도교수 의견서

## 지도교수 의견 (요약)

| | |
|:---|:---|
| **프로젝트** | Conflict-Aware PA-RAG — PA-RAG가 다루지 않은 knowledge conflict를 preference learning으로 정렬 |
| **지도교수** | 황의원 · **팀 03** Alltology |

**연구 방향 · 진행**
- PA-RAG 미해결 지점(knowledge conflict)을 정확히 짚어 문제 설정이 **타당**
- 매주 토요일 정기 회의·여름방학 면담 일정 등 **권고 일정을 충실히 이행**
- 지도 방향: ① 단순 성능 비교 → **한계·유형 분석** framing ② **범위 명시적 제한**(LoRA, conflict type 3~4개) ③ **공개 벤치마크 우선**·자연 conflict는 case study

**현재 성과 · 향후 과제**
- Base RAG · conflict-aware prompting **동일 코드베이스 구현 완료**, phi-2 파일럿으로 **초기 신호 확인**
- 연구 페이지·데모 **직접 구축·공개** — 구현·협업 역량 **높이 평가**
- 벤치마크(ClashEval · ConflictBank · WikiContradict)·연산 자원 **확보** — 핵심 과제는 **방법론 정합성**(resolution rule, synthetic→natural 전이, trade-off)
- 여름방학 면담으로 단계 점검 · general → 도메인 확장 · **ACL/EMNLP/NAACL** 등 장기 목표

<div class="highlight">
<b>종합:</b> 기반 논문의 명확한 확장점, 정직한 범위 설정, 충실한 사전 구현을 갖추어 <b>졸업프로젝트로서 적절</b>하다고 판단함.
</div>

<p class="sign">지도교수 &nbsp; 황의원</p>

---

<!-- _class: title -->

# 감사합니다

<p>
GitHub: <a href="https://github.com/Ontology0/Graduation-Project" style="color:#F9EEEB">github.com/Ontology0/Graduation-Project</a><br/>
데모 사이트: <a href="http://alltology.zapto.org" style="color:#F9EEEB">alltology.zapto.org</a><br/>
데모 영상: <a href="https://youtu.be/qc0GkgJoBBk" style="color:#F9EEEB">youtu.be/qc0GkgJoBBk</a><br/>
HuggingFace: <a href="https://huggingface.co/spaces/ponyo03/conflict-aware-rag-demo" style="color:#F9EEEB">ponyo03/conflict-aware-rag-demo</a><br/>
<br/>
팀 03 · Alltology · 박세령 (2276121) · 손현경 (2329019) · 이다영 (2317022)
</p>
