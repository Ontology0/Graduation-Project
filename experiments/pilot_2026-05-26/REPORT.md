# Local Pilot Validation Report

**일자**: 2025-05-26
**작성자**: (이름)
**연구 주제**: RAG-aware Alignment Tuning — Conflict-aware Prompting Pilot

---

## 1. 목적

본 보고서는 **RAG-aware Alignment Tuning** 연구의 본 실험(Llama 3.1-8B + 전체 데이터셋)에 앞서, 로컬 환경에서 수행한 **파이프라인 검증 및 1차 파일럿 관찰** 결과를 정리한다.

본 단계의 목표는 다음 두 가지로 한정한다.

1. **파이프라인 wiring 검증**: YAML config만 교체하여 Base RAG와 Conflict-aware Prompting을 동일 코드베이스에서 비교할 수 있는지 확인
2. **방법론 작동 신호 확인**: 동일 retrieval/generation 설정 하에서 프롬프트 차이가 답변에 의미 있는 변화를 만드는지 여부에 대한 anecdotal 관찰

본 보고서는 **방법론의 효과를 입증하지 않는다**. 본 실험으로 가기 전 sanity check 결과를 공유하는 것이 목적이다.

---

## 2. 실험 셋업

### 2.1 환경

| 항목 | 값 |
|---|---|
| OS | Windows 11 |
| Python | 3.13 |
| 디바이스 | CPU only (로컬 검증용) |
| Generator | `microsoft/phi-2` (2.7B) |
| Embedder | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store | FAISS (CPU) |

> ⚠️ **phi-2는 본 실험 대상 모델이 아니다.** 본 실험은 Llama 3.1-8B를 사용하며, 본 단계에서 phi-2를 쓴 이유는 로컬 CPU에서 빠르게 파이프라인을 검증하기 위함이다. phi-2의 출력 품질(특히 EOS 안정성)은 본 실험 결과에 일반화되지 않는다.

### 2.2 비교 대상

두 arm은 **prompt_file을 제외한 모든 설정이 동일**하다.

| 항목 | Base RAG | Conflict-aware Prompting |
|---|---|---|
| Generator model | phi-2 | phi-2 |
| Embedder | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 |
| `top_k` | 5 | 5 |
| `chunk_size` / `overlap` | 512 / 128 | 512 / 128 |
| Generation | max_new_tokens=256, do_sample=False | (동일) |
| **Prompt** | `configs/prompts/base_rag.md` | `configs/prompts/conflict_aware.md` |

두 프롬프트의 핵심 차이는 다음과 같다.

- **Base RAG**: "Use the context above when it supports your answer" 수준의 일반적 RAG 지시
- **Conflict-aware**: 충돌 명시적 인지 → 우선순위 규칙(authoritative / time-valid / source label 기반) → time, condition, source 명시 요구

### 2.3 데이터

자체 작성한 합성 conflict 데이터셋 (`data/synthetic_conflicts/pilot_conflicts.jsonl`) 10케이스 중 **앞 2케이스**를 사용했다.

| Conflict Type | 케이스 수 | 비고 |
|---|---|---|
| temporal | 4 | 시간 경과로 정보 갱신 |
| version_update | 3 | 명시적 정정/개정 |
| source_disagreement | 3 | 동시간대 출처 간 불일치 |

각 케이스는 `outdated` 문서 1개 + `current` 문서 1개 + `distractor` 1~2개로 구성된다. 데이터셋 스키마와 stance 정의는 `data/synthetic_conflicts/README.md` 참고.

---

## 3. 결과

### 3.1 Case 001 — Temporal (로고 색상 변경)

**질문**: What is the official primary color of the Helios Research Consortium logo after the 2024 brand refresh?

**Gold Answer**: solar amber (#F0A202)

**Retrieved (두 arm 동일)**:

| Rank | Source | Score | Stance |
|---|---|---|---|
| 1 | d2 (2024 Refresh Memo) | 0.811 | current |
| 2 | d1 (2021 Brand Guide) | 0.803 | outdated |
| 3 | d3 (IT Security Policy) | 0.200 | distractor |

| Arm | 정답 여부 | 생성 토큰 | 비고 |
|---|---|---|---|
| Base RAG | ✅ solar amber | 256 (max) | 답변 후 가짜 User/Assistant 대화 및 논리 퍼즐 생성 (환각) |
| Conflict-aware | ✅ solar amber | **101** (자연 종료) | 답변 후 환각 없음 |

**관찰**:

두 arm 모두 정답에 도달했다. 차이는 답변 이후 행태에서 나타났다. Conflict-aware arm은 답변을 마치고 EOS를 뱉어 자연스럽게 종료된 반면, Base arm은 max_tokens까지 환각된 대화를 채웠다.

다만 Conflict-aware의 추론 자체에는 오류가 있었다. 답변 중 "Both sources indicate that the primary logo color should be solar amber"라고 했는데, 실제로 d1(2021 Brand Guide)은 cobalt blue를 명시하고 있다. 최종 답은 맞았으나 중간 추론은 부정확했다. **답이 맞았다고 추론이 옳다고 볼 수 없는 사례.**

### 3.2 Case 002 — Version Update (배터리 용량 정정) ⭐

**질문**: What is the rated battery capacity of the Orinex Phone Model Z according to the current product specification?

**Gold Answer**: 4800 mAh (2024 Errata에서 정정)

**Retrieved (두 arm 동일)**:

| Rank | Source | Score | Stance |
|---|---|---|---|
| 1 | d2 (2024-01 Errata v2.2, "corrected to 4800") | 0.846 | current |
| 2 | d1 (2023-06 Spec Sheet v2.1, "5000") | 0.839 | outdated |
| 3 | d3 (Accessories Catalog) | 0.608 | distractor |
| 4 | d4 (Corporate History) | 0.149 | distractor |

| Arm | 답변 | 정답 여부 |
|---|---|---|
| Base RAG | **5000 mAh** | ❌ |
| Conflict-aware | **4800 mAh** | ✅ |

**관찰**:

본 케이스는 retrieval 단계에서 outdated와 current가 거의 동일한 점수로 상위에 등장했고(0.846 vs 0.839), generator 단계에서 어느 쪽을 채택할지가 답을 갈랐다.

- **Base arm**: d1(outdated, "5000 mAh")을 그대로 인용하여 5000 mAh로 답했다. "Errata", "corrected", 2024 vs 2023 같은 정정 신호를 활용하지 못했다.
- **Conflict-aware arm**: "The previous product specification sheet (2023-06) stated a rated battery capacity of 5000 mAh, but this claim is now corrected"라고 명시적으로 정정 관계를 인지하고 4800 mAh를 답했다.

본 단계에서 관찰한 anecdotal evidence 중 가장 명확한 사례. 동일한 retrieval 결과가 동일 모델에 들어갔는데도 **프롬프트 차이만으로 정답이 뒤집힌 케이스**이다.

### 3.3 부수적 관찰

- **Distractor 처리**: 두 arm 모두 distractor 문서(IT 보안 정책, 회사 연혁)는 답변에 거의 영향을 주지 않았다. Retrieval 점수도 일관되게 낮았다.
- **phi-2의 EOS 불안정성**: Base arm은 두 케이스 모두 max_new_tokens(256)까지 생성을 멈추지 않고 가짜 대화/퀴즈를 만들었다. 본 실험에서 Llama 3.1-8B로 가면 줄어들 가능성이 높지만, 평가 시 stop token 또는 첫 문장/문단 추출 같은 후처리가 필요할 수 있다.
- **Prompt 길이**: Conflict-aware 프롬프트는 token 기준 약 1.5배 길다(283 vs 432). 본 실험에서 비용/효과 trade-off로 다뤄야 할 항목.

---

## 4. 한계와 정직한 해석

본 결과는 **방법론의 효과 입증이 아니다.** 다음 한계를 분명히 한다.

1. **n=2**: 통계적 의미 없음. 다른 8개 케이스에서 반대 방향의 결과가 나올 수 있다.
2. **phi-2 ≠ Llama 3.1-8B**: 본 실험 모델이 아닌 더 작고 약한 모델이다. phi-2가 outdated 문서에 약한 것이 Llama에서도 재현될지 불확실하다.
3. **합성 데이터셋의 conflict 신호가 명시적**: "Effective immediately", "corrected", "Errata" 같은 단어가 의도적으로 들어가 있다. 실제 retrieval 환경의 noisy한 conflict와는 다르다.
4. **Conflict-aware arm의 추론 오류 존재**: Case 001에서 보았듯, 답이 맞아도 추론 과정은 부정확할 수 있다. 평가 메트릭이 정답만 측정하면 이런 약점을 놓친다.

따라서 본 결과는 "방법론이 작동한다"가 아니라 **"본 실험을 진행할 만한 신호가 있다"** 정도로 해석한다.

---

## 5. 다음 단계

### 5.1 즉시 다음 (본 실험 준비)

- [ ] Colab + GPU 환경 셋업 (T4 또는 L4)
- [ ] Llama 3.1-8B 로드 (가능하면 4-bit quantization)
- [ ] HuggingFace 캐시를 Google Drive에 연결 (세션 재개 시 재다운로드 방지)
- [ ] 전체 10케이스 × 2 arm 실행
- [ ] 결과 JSONL을 Drive에 저장

### 5.2 평가 메트릭 정의 (Colab 실행 전 결정 필요)

본 데이터셋 특성상 다음 메트릭을 검토 중이다.

- **Gold answer substring match**: 단순하지만 phi-2 결과에서 본 환각 토큰 때문에 false positive 가능
- **Stance accuracy**: 모델이 current 문서를 인용했는지, outdated 문서를 인용했는지 분류
- **LLM-as-judge**: GPT-4 또는 Claude에게 정답성/추론품질 동시 평가 요청

본 실험 전에 1~2개 메트릭으로 확정할 예정.

### 5.3 본 보고서 이후 확장 (mid-term 발표 전까지)

- 합성 케이스 수 확대 (10 → 30~50)
- Conflict type별 결과 분리 분석 (temporal vs version_update vs source_disagreement)
- (논의 후) LoRA fine-tuning arm 추가 — 본 연구의 핵심 차별점 (PA-RAG 대비 lightweight tuning)

---

## 6. 재현 방법

```powershell
# 환경 셋업
.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."

# 1) 검증 스크립트 (모델 로드 없거나 가벼움)
python experiments/pilot_2025-05-26/01_check_config.py
python experiments/pilot_2025-05-26/02_diff_prompts.py
python experiments/pilot_2025-05-26/04_check_dataset.py

# 2) 단일 케이스 e2e (phi-2 로딩, ~2분)
python experiments/pilot_2025-05-26/03_e2e_real.py

# 3) 배치 실행 (2케이스, ~5분/arm)
python scripts/run_batch.py \
  --config configs/experiments/rag_base.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl \
  --limit 2

python scripts/run_batch.py \
  --config configs/experiments/prompting_conflict_aware.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl \
  --limit 2
```

결과 파일은 `experiments/pilot_2025-05-26/results/`에 보존되어 있다.

---

## 7. 참고

- 데이터셋 스키마 및 stance 정의: `data/synthetic_conflicts/README.md`
- Base RAG 프롬프트: `configs/prompts/base_rag.md`
- Conflict-aware 프롬프트: `configs/prompts/conflict_aware.md`
- 본 연구의 핵심 reference: PA-RAG (Wu et al., 2024, arXiv:2412.14510)
