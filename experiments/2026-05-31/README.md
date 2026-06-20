# Conflict Handling Experiments — 2026-05-31

본 디렉터리는 RAG knowledge conflict 상황에서 **conflict-aware prompting**이
효과가 있는지를 점진적으로 검증한 하루치 실험 묶음이다.
실험은 exp1 → exp4로 갈수록 연구 질문(RQ)에 가깝게 초점을 좁혀갔다.

> ⚠️ 본 실험들은 **API 모델(gpt-4o-mini, Claude haiku)** 기반 파일럿이다.
> 본 연구 대상인 Llama 3.1-8B 실험의 사전 탐색 단계이며, 결과는 그 맥락에서 해석한다.

---

## 실험 흐름 한눈에

| 실험 | 초점 | 모델 | 핵심 결과 |
|---|---|---|---|
| exp1 | 거짓 문서 vs 모델 지식 (기본) | gpt-4o-mini | conflict-aware가 거짓 거부에 우세 (설계 24케이스, **채점 12케이스**) |
| exp2 | A/B/C 타입 분해 | claude-haiku | 효과는 "정답 문서 부재 시 robustness"에 한정 |
| exp3 | temporal update (명시적) | claude-haiku | 두 arm 모두 100% (천장 효과) |
| exp4 | temporal update (암묵적) | claude-haiku | 두 arm 모두 100% (천장 효과) |

---

## 연구 흐름 (왜 이 순서로 갔는가)

1. **exp1**: conflict-aware가 효과 있어 보임 (거짓 문서를 더 잘 거부).
2. **exp2**: 같은 사실을 A/B/C 문서 구성으로 분해해보니, 효과는
   "검색이 실패해 거짓 문서만 있을 때(A)"에 한정됨을 발견.
   동시에, 이 설계가 **메인 RQ와 초점이 다름**을 인지
   (exp1-2는 "거짓 거부", RQ는 "최신 수용" — 방향이 반대).
3. **exp3**: 메인 RQ인 temporal update로 재설계
   (내부 옛 지식 vs 외부 최신 정보). 그러나 문서가 변화를 직접 설명해
   충돌이 약했고, 두 arm 모두 100%.
4. **exp4**: 문서가 변화를 설명하지 않고 최신 사실을 전제만 하도록
   ("암묵적 충돌") 강화. 그래도 두 arm 모두 100%.

---

## 가장 중요한 통찰: 천장 효과 (Ceiling Effect)

> **강한 모델(gpt-4o-mini, Claude haiku)은 temporal conflict를 프롬프트
> 도움 없이도 거의 100% 해결한다.**

따라서 강한 모델로는 Base vs Conflict-aware의 차이를 변별할 수 없다.
이는 실패가 아니라 **upper bound를 확정한 결과**다:

```
강한 모델 (gpt-4o-mini, Claude)  → ~100%  = "이 문제는 풀 수 있다" (upper bound)
약한 모델 (phi-2, exp1에서 실패)  → 낮음    = lower bound
본 연구 대상 (Llama 3.1-8B)       → ?       = 진짜 측정 대상
```

→ **본 연구의 기여**: 작은 모델(Llama-8B)을 LoRA/DPO로 강한 모델 수준의
conflict 처리 능력까지 끌어올릴 수 있는가.

---

## 방법론적 교훈

- **데이터 설계가 결과를 좌우한다**: 문서가 변화를 친절히 설명하면(exp3)
  충돌이 약해진다. 진짜 충돌은 암묵적 전제(exp4)로 만들어야 한다.
- **RQ와 실험의 정렬**: exp1-2는 "거짓 거부", 메인 RQ는 "최신 수용".
  방향이 반대였음을 exp2에서 발견하고 exp3-4에서 교정.
- **평가 메트릭 한계**: substring 매칭은 짧은 답(예: "X")에서 false positive
  위험. 강한 모델 천장 효과로 변별 자체가 어려움.

---

## 추후 진행 방향

1. **(1순위) Llama 3.1-8B로 동일 실험** — 천장 효과 없는 타겟 모델에서
   baseline 측정. GPU 필요.
2. **충돌 강도 강화** — 문서 1개 + distractor는 모델이 쉽게 신뢰.
   복수 문서 불일치 / 모델이 강하게 믿는 사실의 미묘한 충돌 등.
3. **평가 메트릭 정교화** — substring → LLM-as-judge 등.
4. **(본 연구 핵심) LoRA/DPO 학습** — conflict 처리를 학습으로 내재화.

---

## 폴더 구성

```
2026-05-31/
├── README.md                  ← (이 파일) 종합 요약
├── exp1_clasheval_basic/      ← 거짓 문서 판별 (gpt-4o-mini)
├── exp2_abc_types/            ← A/B/C 타입 분해
├── exp3_temporal_update/      ← temporal, 명시적 충돌
└── exp4_temporal_implicit/    ← temporal, 암묵적 충돌
```

각 폴더의 README에 실험 설계·결과·해석이 정리되어 있다.

---

## 환경

- API: OpenAI (gpt-4o-mini) / LiteLLM 경유 Claude (haiku)
- 실행: Google Colab
- 데이터: 자체 합성 (각 폴더의 build_*.py로 재현 가능)

## 관련 이슈
- #38 (exp1, exp2), #39 (exp3, exp4)
