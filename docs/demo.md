# Demo / Quickstart

> 목적: 평가자/외부 방문자가 “이 레포에 **실제로 돌아가는 코드**가 있다”는 걸 빠르게 확인할 수 있게, **smoke test**와 **증빙(예시 로그/결과 형태)**를 한 곳에 모읍니다.  
> Status: Start-stage 연구 산출물입니다. Arm 1·2 파일럿·로컬 smoke 결과는 존재하며, 5-arm 정량 벤치마크는 Growth 단계입니다.

## Quick run (smoke test)

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

### 성공 기준(무엇을 보면 “성공”인가?)

- 콘솔에 `Experiment:` / `Question:` / `Answer:` / `Sources:`가 출력된다
- 실행 후 `outputs/runs/` 아래에 결과 파일이 생성된다(JSON/MD)

## Expected outputs (captured 2026-05-31)

실제 실행 결과 (phi-2, CPU):

```
Experiment: base_rag

Question: What is knowledge conflict in RAG?

Answer: Knowledge conflict in RAG refers to situations where there is a
discrepancy between two pieces of information or sources that are related
to each other. ... (이하 생략)

Sources:
  - [knowledge_conflict.md#chunk0] (score: 0.6396)
  - [README.md#chunk0] (score: 0.2724)
  - [example_conflict.txt#chunk1] (score: 0.2633)
  - [example_conflict.txt#chunk2] (score: 0.1863)
  - [example_conflict.txt#chunk0] (score: 0.1748)

Saved run:
  - JSON: outputs/runs/20260531T104426Z.json
  - MD:   outputs/runs/20260531T104426Z.md
```

생성된 결과 파일:
- `outputs/runs/20260531T104426Z.json`
- `outputs/runs/20260531T104426Z.md`

## Evidence (captured example)

실제 로컬 실행 결과 (2026-05-31, macOS / Python 3.12, phi-2 on MPS):

```
Experiment: base_rag

Question: What is knowledge conflict in RAG?

Answer: Knowledge conflict in RAG refers to situations where there is a discrepancy
between two pieces of information or sources that are related to each other. ...
This conflict arises because the retrieved evidence contradicts the model's parametric answer.

Sources:
  - [knowledge_conflict.md#chunk0] (score: 0.6396)
  - [README.md#chunk0] (score: 0.2724)
  - [example_conflict.txt#chunk1] (score: 0.2633)
  - [example_conflict.txt#chunk2] (score: 0.1863)
  - [example_conflict.txt#chunk0] (score: 0.1748)

Saved run:
  - JSON: outputs/runs/smoke_test_base_rag.json
  - MD:   outputs/runs/smoke_test_base_rag.md
```

결과 파일: [`outputs/runs/smoke_test_base_rag.json`](../outputs/runs/smoke_test_base_rag.json) · [`outputs/runs/smoke_test_base_rag.md`](../outputs/runs/smoke_test_base_rag.md)

## Demo goal (final presentation)

Show a **context–memory conflict** scenario where retrieved evidence and the model’s default answer disagree, and compare how each method resolves the conflict (or abstains).

## Demo scenario (Start-stage implemented)

- **Setting:** Single user question with one retrieved passage that contradicts the answer the base model would give without conflict instructions.
- **Example type:** Fictional or clearly labeled synthetic domain (no real-world entity claims requiring verification).
- **Sample document:** `data/sample_docs/example_conflict.txt`
- **Question:** `What color is the Northwood Institute mascot after the 2019 revision?`
- **Conflict structure:** parametric answer = deep blue, retrieved evidence = silver-green
- **Resolution rule:** when the question targets the post-2019 revision, prefer the retrieved appendix evidence.

This demo is a **qualitative smoke scenario**, not a final benchmark.

## Compared methods

| Method | Config / prompt |
|--------|-----------------|
| Base RAG | `configs/experiments/rag_base.yaml`, `configs/prompts/base_rag.md` |
| Conflict-aware prompting | `configs/experiments/prompting_conflict_aware.yaml`, `configs/prompts/conflict_aware.md` |
| PA-RAG-style LoRA | `configs/experiments/lora_parrag_style.yaml` (when trained) |
| Conflict-Aware RAG LoRA | `configs/experiments/lora_conflict_only.yaml` (when trained) |
| Conflict-Aware PA-RAG LoRA | `configs/experiments/lora_conflict_parrag.yaml` (when trained) |

## Demo result table (pilot runs, 2026-05-31)

질문: *"What color is the Northwood Institute mascot [after the 2019 revision]?"*  
문서: `data/sample_docs/example_conflict.txt` (parametric=deep blue, retrieved=silver-green)

| Method | Follows evidence? | States conflict? | Resolution correct? | Notes |
|--------|-------------------|------------------|---------------------|-------|
| Base RAG | △ (silver-green 언급하나 확실히 선택 안 함) | ✅ 충돌 서술 | △ 불명확 | `outputs/runs/smoke_test_conflict_base.md` |
| Conflict-aware prompting | ✅ retrieved 우선 | ✅ 충돌 명시 | ✅ | `outputs/runs/smoke_test_conflict_aware.md` |
| PA-RAG-style LoRA | — | — | — | 학습 미완 |
| Conflict-Aware RAG LoRA | — | — | — | 학습 미완 |
| Conflict-Aware PA-RAG LoRA | — | — | — | 학습 미완 |

*LoRA 결과는 학습 완료 후 업데이트 예정. 정량 RAGAS 스코어 미측정.*

### Local phi-2 smoke vs API-model pilot

The local phi-2 smoke output (`outputs/runs/smoke_test_conflict_aware.*`) verifies **retrieval/prompt wiring** and shows that the correct evidence is retrieved. It is **not** used as the main answer-quality benchmark.

The answer-quality claim is based on the **API-model pilot experiments** in `experiments/2026-05-31/`.

## Demo video

- **URL:** https://youtu.be/qc0GkgJoBBk

## Notes for final presentation

- Emphasize **context–memory** scope; inter-context and intra-memory are out of main scope.
- State clearly that results are **pilot / preliminary** until benchmark eval is complete.
- Link to `docs/experiment_design.md` and `outputs/` for reproducible run folders when available.
