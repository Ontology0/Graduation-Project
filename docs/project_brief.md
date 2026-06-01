# Project Brief — Conflict-Aware PA-RAG

> **팀:** 03팀 Alltology · **트랙:** 연구 · **지도교수:** 황의원 교수님  
> **팀원:** 박세령 · 손현경 · 이다영 · **작성일:** 2026-06-02

---

## 문제 정의

RAG(Retrieval-Augmented Generation)는 외부 문서를 검색해 LLM 답변의 정확성을 높이는 방식이다. 그런데 **검색된 문서와 모델의 파라미터 지식이 서로 다른 답을 가리킬 때**, 모델은 어느 쪽을 따라야 할지 판단하지 못한다.

| 충돌 상황 | 바람직한 행동 | 현재 RAG의 문제 |
|---|---|---|
| 외부 문서가 최신·권위 정보 | 외부 근거 우선 | 내부 지식 고집 |
| 외부 문서가 부정확·모호 | 내부 지식 or 불확실성 표현 | 외부 문서 맹신 |
| 둘 다 불확실 | abstention / 한계 명시 | 확신 있는 오답 |

기존 PA-RAG는 informativeness·robustness·citation quality를 정렬 축으로 다루지만, **context–memory conflict를 명시적 학습 목표로 다루지 않는다.** 이것이 본 연구의 출발점이다.

---

## 고객 및 가치 제안

**고객 세그먼트**

- 기업 내부 문서 RAG 운영팀 (정책·매뉴얼 — 버전 충돌 빈번)
- 법률·의료·금융 도메인 RAG 개발자 (오답의 위험이 높은 영역)
- LLM 신뢰성 연구자 (conflict resolution 측정 및 개선)

**가치 제안**

프롬프트 수준의 conflict-aware 지시는 강한 API 모델에서는 효과가 있으나, 소형 오픈소스 모델(Llama 3.1-8B)에서는 gap이 존재할 것으로 예상된다. DPO + LoRA로 conflict resolution 능력을 모델에 **학습으로 내재화**하면, 프롬프트 의존 없이 강건하고 일반화 가능한 처리가 가능하다는 것이 본 연구의 핵심 주장이다.

---

## 솔루션 및 차별성

5개 arm을 비교해 "프롬프트 지시"와 "학습 내재화"의 효과를 분리 측정한다.

| # | 방법 | 학습 | 역할 |
|---|------|:----:|------|
| 1 | Base RAG | — | 하한선 |
| 2 | Conflict-Aware Prompting | — | 프롬프트만으로 충돌 처리 (비학습 상한선) |
| 3 | PA-RAG-style LoRA | DPO + LoRA | conflict 없이 PA-RAG식 정렬 |
| 4 | Conflict-Aware RAG LoRA | DPO + LoRA | conflict preference만 학습 |
| 5 | **Conflict-Aware PA-RAG LoRA** ⭐ | DPO + LoRA | PA-RAG + conflict 통합 (제안 방법) |

**기존 연구 대비 차별점**

| 비교 | 차이 |
|------|------|
| 기존 PA-RAG | conflict resolution 축 없음 |
| Prompting 접근 | 소형 모델에서 효과 불안정, 프롬프트 의존 |
| RAG-Fusion / HyDE | 검색 품질 개선 — conflict *판단 학습* 아님 |
| **본 연구** | DPO + LoRA로 conflict resolution을 **학습 목표로 명시**, 5-arm 분리 측정 |

---

## 파일럿 실험 결과

> 파일럿 대상: gpt-4o-mini, claude-haiku (강한 API 모델). 본 연구 타겟인 Llama 3.1-8B 탐색의 사전 검증 단계.  
> 상세: [`experiments/2026-05-31/`](experiments/2026-05-31/)

**exp1 — 거짓 문서 거부율** (gpt-4o-mini, 24케이스)

| Arm | 전체 정확도 | 거짓 문서 거부 |
|-----|:---------:|:------------:|
| Base RAG | 75% | 3 / 6 |
| Conflict-Aware Prompting | **100%** | **6 / 6** |

**exp2 — 문서 구성별 분해** (claude-haiku, 36케이스)

| 문서 구성 | Base RAG | Conflict-Aware |
|----------|:--------:|:--------------:|
| A: 거짓만 (정답 없음) | 50% | **83%** |
| B: 거짓 + 정답 공존 | 100% | 100% |

**핵심 발견:** 강한 API 모델에서는 conflict-aware prompting이 유효하나 천장 효과 존재.  
→ **Llama 3.1-8B에서 Base RAG와 Conflict-Aware 간 gap이 클 것으로 예상** — 학습 내재화의 필요성을 측정하는 본 연구의 핵심 구간.

---

## 연구 범위 및 단계

| 단계 | 내용 | 상태 |
|------|------|:----:|
| **Start** (이번 학기) | 문제 정의 · RAG 파이프라인 구현 · 파일럿 실험 (Arm 1·2) · 개선 가능성 검증 | ✅ 완료 |
| **Growth** (확장) | Llama 3.1-8B 대규모 DPO+LoRA 학습 · ClashEval / WikiContradict 5-arm 정량 벤치마크 | 🔄 예정 |

> DPO+LoRA 코드(`src/training/train.py`)는 dry-run 수준에서 동작 확인 완료 (train_loss=0.693, epoch=0.5).  
> 대규모 학습 및 정량 비교는 Growth 단계 범위.

---

*AI 도구 활용 내역: [docs/ai_transparency_report.md](ai_transparency_report.md)*
