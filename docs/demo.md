# Demo / Quickstart

> 목적: 평가자/외부 방문자가 “이 레포에 **실제로 돌아가는 코드**가 있다”는 걸 빠르게 확인할 수 있게, **smoke test**와 **증빙(예시 로그/결과 형태)**를 한 곳에 모읍니다.  
> Status: 연구 레포 **scaffold** 단계이며, 최종 벤치마크/정량 결과는 아직 없습니다.

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

> 아직 영상/스크린샷을 레포에 포함하지 않는 대신, **재현 가능한 관찰 포인트**를 고정합니다.  
> 캡처를 추가할 경우, 개인키/토큰/챗ID 등 민감정보가 노출되지 않게 주의합니다.

- CLI 실행 시 출력되는 “Saved run” 경로
  - 예: `Saved run: JSON: outputs/runs/...  MD: outputs/runs/...`

## Demo goal (final presentation)

Show a **context–memory conflict** scenario where retrieved evidence and the model’s default answer disagree, and compare how each method resolves the conflict (or abstains).

## Demo scenario (planned)

- **Setting:** Single user question with one retrieved passage that contradicts the answer the base model would give without conflict instructions.
- **Example type:** Fictional or clearly labeled synthetic domain (no real-world entity claims requiring verification).
- **Sample document:** `data/sample_docs/example_conflict.txt` (fictional Northwood Institute mascot color revision).
- **To be updated:** Concrete question, context block, and resolution rule once a pilot dataset slice exists.

## Compared methods

| Method | Config / prompt |
|--------|-----------------|
| Base RAG | `configs/experiments/rag_base.yaml`, `configs/prompts/base_rag.md` |
| Conflict-aware prompting | `configs/experiments/prompting_conflict_aware.yaml`, `configs/prompts/conflict_aware.md` |
| PA-RAG-style LoRA | `configs/experiments/lora_parrag_style.yaml` (when trained) |
| Conflict-Aware RAG LoRA | `configs/experiments/lora_conflict_only.yaml` (when trained) |
| Conflict-Aware PA-RAG LoRA | `configs/experiments/lora_conflict_parrag.yaml` (when trained) |

## Demo result table (template; fill after runs)

| Method | Follows evidence? | States conflict? | Resolution correct? | Notes |
|--------|-------------------|------------------|---------------------|-------|
| Base RAG | TBD | TBD | TBD | |
| Conflict-aware prompting | TBD | TBD | TBD | |
| PA-RAG-style LoRA | TBD | TBD | TBD | |
| Conflict-Aware RAG LoRA | TBD | TBD | TBD | |
| Conflict-Aware PA-RAG LoRA | TBD | TBD | TBD | |

*No numeric scores — fill after live demo runs.*

## Demo video

- **URL:** `TODO` (e.g., presentation recording link)

## Notes for final presentation

- Emphasize **context–memory** scope; inter-context and intra-memory are out of main scope.
- State clearly that results are **pilot / preliminary** until benchmark eval is complete.
- Link to `docs/experiment_design.md` and `outputs/` for reproducible run folders when available.
