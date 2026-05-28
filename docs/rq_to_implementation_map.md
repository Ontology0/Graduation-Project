# RQ ↔ Implementation Map

> 목적: `README.md`(문제/가설) ↔ `docs/*`(설계) ↔ `configs/*`(실험 설정) ↔ `src/*`/`scripts/*`(구현) 간 **정합성(Alignment)**을 평가자 관점에서 빠르게 점검할 수 있도록 연결합니다.  
> Status: 본 레포는 연구 **scaffold**이며, 측정 결과/점수는 아직 없습니다.

## Snapshot: what exists vs. what is planned

- **Implemented (first draft)**: Base RAG 파이프라인 (`src/rag/`) + CLI 실행 (`scripts/run_pipeline.py`) + repo 문서 기반 Telegram RAG bot (`src/chatbot/telegram_bot.py`)
- **Planned / scaffolded**: DPO+LoRA 학습 (`src/training/`), 평가 파이프라인 (`src/evaluation/`), conflict-aware prompting/LoRA arms별 config
- **TBD**: 최종 벤치마크/평가 지표/프로토콜 (see `docs/benchmark_selection.md`, `docs/decision_log.md`)

## Research questions (from `README.md`, `docs/research_plan.md`)

### RQ1. Preference learning으로 conflict resolution을 내재화할 수 있는가?

- **Concept / definition**
  - `docs/research_plan.md` (Target: context–memory conflict)
  - `docs/experiment_design.md` (comparison arms)
- **Baselines**
  - Base RAG (no training): `configs/experiments/rag_base.yaml`
  - Conflict-aware prompting (planned): `configs/experiments/prompting_conflict_aware.yaml`, `configs/prompts/conflict_aware.md`
- **Preference learning (planned)**
  - Training entrypoint: `src/training/train.py`
  - Preference schema: `data/schema/preference_pair.schema.json`
  - LoRA arms configs (planned):
    - `configs/experiments/lora_parrag_style.yaml`
    - `configs/experiments/lora_conflict_only.yaml`
    - `configs/experiments/lora_conflict_parrag.yaml`

### RQ2. 어떤 conflict pattern이 학습되고 어떤 것은 한계인가?

- **Conflict scope**
  - In-scope: context–memory conflict (README “연구 범위” / `docs/research_plan.md`)
  - Out-of-scope (main line): inter-context / intra-memory (README / `docs/decision_log.md`)
- **Planned analysis hooks**
  - Per-run artifacts under `outputs/` (see `outputs/.gitkeep`)
  - Qualitative error analysis template referenced in `docs/experiment_design.md` (planned)

### RQ3. Prompting 대비 LoRA 내재화는 얼마나 효과적인가?

- **Design**
  - Prompt-only arm vs. LoRA arms 비교 구도: `docs/experiment_design.md`
- **Implementation touchpoints**
  - Prompting: `configs/prompts/conflict_aware.md` (planned)
  - LoRA: `src/training/train.py` (scaffold) + LoRA configs (planned)
- **How to run (today)**
  - Prompting/LoRA는 아직 “실험 결과”가 아니라 scaffold 상태이므로, 현재는 Base RAG CLI로 파이프라인 wiring을 확인:
    - `scripts/run_pipeline.py --config configs/experiments/rag_base.yaml --docs data/sample_docs/ --question ...`

### RQ4. Conflict 정렬이 다른 축(informativeness/robustness/citation)을 해치지 않는가?

- **Intended comparison**
  - PA-RAG-style vs conflict-only vs combined arms: `docs/experiment_design.md`
- **Evaluation status**
  - Metrics/protocol: TBD (`docs/benchmark_selection.md`, `src/evaluation/evaluate.py` scaffold)

## “실제 동작하는 코드” 빠른 링크(Repo rubric 대응)

- **RAG CLI 엔트리포인트**: `scripts/run_pipeline.py`
- **RAG 파이프라인 핵심**: `src/rag/pipeline.py` (+ `src/rag/*` 모듈)
- **Telegram bot 엔트리포인트**: `scripts/telegram_bot.py` → `src/chatbot/telegram_bot.py`
- **운영/보안 메모**: `docs/telegram_bot_ops.md`

## Related “alignment” documents

- `docs/architecture.md` (1-page system view)
- `docs/demo.md` (smoke test + demo evidence)
- `docs/verification_checklist.md` (repro/ops checks)
- `docs/ai_transparency_report.md` (AI usage transparency)
