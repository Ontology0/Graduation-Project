# API Pilot — Conflict Handling on a Strong Model

**일자**: 2026-05-28
**모델**: `gpt-4o-mini` (OpenAI API)
**연구 주제**: RAG-aware Alignment Tuning — Conflict-aware Prompting Pilot (2차)

---

## 1. 목적

1차 파일럿(`experiments/pilot_2025-05-26/`, phi-2 로컬)에 이어, **강한 모델(gpt-4o-mini)**을 API로 호출하여 동일한 합성 conflict 데이터셋에서 Base RAG와 Conflict-aware Prompting을 비교한다.

본 실험의 목적은 **upper bound 확인**이다. 작은 모델(phi-2)이 conflict 처리에 약했다면, 강한 모델은 어디까지 잘하는지를 측정하여 본 연구 대상(Llama 3.1-8B)의 위치를 가늠한다.

본 실험은 RAG-aware DPO의 효과를 입증하지 않으며, 모델 규모에 따른 conflict 처리 능력의 양 끝점을 잡는 reference 측정이다.

---

## 2. 셋업

| 항목 | 값 |
|---|---|
| 실행 환경 | Google Colab (CPU, API 호출) |
| Generator | `gpt-4o-mini` |
| Retrieval | 생략 (케이스당 문서 3~4개를 전체 context로 투입) |
| Generation | max_tokens=256, temperature=0.2 |
| 데이터 | `data/synthetic_conflicts/pilot_conflicts.jsonl` (10케이스) |

> ⚠️ 본 실험은 retrieval 단계를 생략했다. 케이스당 문서 수가 적어(3~4개) 검색의 의미가 작고, 본 실험의 초점이 generator의 conflict 처리이기 때문이다. 본 실험(full pipeline)에서는 retrieval을 포함한다.

### 비교 대상 (1차와 동일)

| | Base RAG | Conflict-aware |
|---|---|---|
| Generator | gpt-4o-mini | gpt-4o-mini |
| Prompt | `configs/prompts/base_rag.md` | `configs/prompts/conflict_aware.md` |

프롬프트를 제외한 모든 설정이 동일하다.

---

## 3. 결과

### 3.1 정답률: 두 arm 모두 10/10

10케이스 전부에서 두 arm 모두 gold answer의 핵심 수치/사실을 정확히 답했다. 1차에서 phi-2가 case_002(배터리 용량)에서 outdated 문서에 속아 틀렸던 것과 대조적이다.

| 모델 | case_002 정답 여부 | 전체 |
|---|---|---|
| phi-2 (1차) | Base ❌ / CA ✅ | 일부 실패 |
| gpt-4o-mini (2차) | Base ✅ / CA ✅ | 10/10 |

### 3.2 답변 형태의 차이

정답률은 같았으나, 답변의 구조에서 차이가 관찰되었다.

- **Base RAG**: 정답을 즉시 제시하고 근거 문서를 간결히 인용
- **Conflict-aware**: "A conflict exists between..." 형태로 충돌의 존재를 명시하고, 어느 문서가 outdated이고 어느 것이 authoritative한지를 설명한 뒤 답을 제시

예 (case_008, CloudNest 저장 용량):
- Base: "1 TB, errata가 2TB 오타를 정정함" (정답 + 간결)
- Conflict-aware: "launch announcement는 2TB이나, errata가 1TB로 정정" (충돌 구조를 명시적으로 드러냄)

즉 Conflict-aware는 정답성보다 **추론 투명성 / citation quality** 측면에서 차이를 보였다.

---

## 4. 한계와 해석

1. **데이터셋이 너무 쉽다**: 충돌 신호가 "errata", "corrected", "supersedes"처럼 명시적이라 강한 모델은 별다른 추론 없이도 정답에 도달한다. 두 arm 간 변별력이 거의 없다.
2. **정답률만으로는 차이를 못 잡는다**: 두 arm 모두 10/10이므로, 답변 품질(추론 투명성, citation 정확성)을 측정할 별도 메트릭이 필요하다.
3. **채점이 수동(육안)이다**: 자동 채점 스크립트가 아직 없다.
4. **retrieval 생략**: 본 실험과 셋업이 다르므로 직접 비교는 제한적이다.

---

## 5. 연구적 함의

본 실험은 모델 규모에 따른 conflict 처리 능력의 윤곽을 보여준다.

```
phi-2 (작은 모델)    → conflict에 약함 (일부 오답)
gpt-4o-mini (강함)   → conflict 잘 처리 (10/10)
Llama 3.1-8B (타겟)  → 이 사이 어딘가 — 본 연구의 측정 대상
```

→ Research Question: **8B 모델에 lightweight tuning(LoRA + RAG-aware DPO)을 적용하면 강한 모델 수준의 conflict 처리에 근접할 수 있는가?**

phi-2와 gpt-4o-mini의 결과가 각각 lower / upper bound 역할을 한다.

---

## 6. 다음 단계

- [ ] 더 어려운 conflict 케이스 설계 (미묘한 충돌 신호, 그럴듯한 outdated 문서)
- [ ] 자동 채점 스크립트 (정답 포함 여부 + 가능하면 stance / citation 측정)
- [ ] Llama 3.1-8B 동일 실험 → phi-2 / Llama / gpt-4o-mini 3-way 비교
- [ ] (이후) full RAG pipeline (retrieval 포함) 으로 확장

---

## 7. 파일 구성

| 파일 | 설명 |
|---|---|
| `run_api_pilot.ipynb` | Colab 실험 노트북 (API 호출, 10케이스 × 2 arm) |
| `results/gpt4o_mini_10cases_2arm.jsonl` | 실험 결과 (20행: 10케이스 × 2 arm) |

### 결과 JSONL 스키마
```json
{
  "case_id": "case_001",
  "question": "...",
  "gold_answer": "...",
  "conflict_type": "temporal | version_update | source_disagreement",
  "predicted_answer": "...",
  "arm": "base_rag | conflict_aware"
}
```

---

## 8. 재현 방법 (요약)

1. OpenAI API 키 발급 + Colab 환경변수 설정
2. 레포 clone, `feat/data` 브랜치에서 데이터셋 체크아웃
3. `configs/prompts/*.md`에서 프롬프트 로드
4. 케이스 문서를 context로 넣어 gpt-4o-mini 호출 (Base / Conflict-aware 각 1회)
5. 결과를 JSONL로 저장

상세 코드는 `run_api_pilot.ipynb` 참고.

---

## 참고

- 1차 파일럿 보고서: `experiments/pilot_2025-05-26/REPORT.md`
- 데이터셋 스키마: `data/synthetic_conflicts/README.md`
- 핵심 reference: PA-RAG (Wu et al., 2024, arXiv:2412.14510)
