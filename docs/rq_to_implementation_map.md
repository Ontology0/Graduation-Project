# RQ ↔ Implementation Map

> 목적: `README.md`(문제/가설) ↔ `docs/*`(설계) ↔ `configs/*`(실험 설정) ↔ `src/*`/`scripts/*`(구현) 간 **정합성(Alignment)**을 평가자 관점에서 빠르게 점검할 수 있도록 연결합니다.  
> Status: 본 레포는 **Start-stage** 연구 산출물입니다. Arm 1·2(Base RAG, Conflict-Aware Prompting)의 API-model 파일럿 결과와 로컬 smoke test 결과는 존재합니다. 다만 Llama 3.1-8B 기반 DPO+LoRA 학습, Arm 3·4·5 adapter inference, 5-arm 정량 benchmark는 **Growth** 단계 범위입니다.

## Snapshot: what exists vs. what is planned

- **Implemented (Start-stage)**: Base RAG 파이프라인 (`src/rag/`) + CLI 실행 (`scripts/run_pipeline.py`) + Conflict-Aware Prompting 비교 (`make demo-conflict`) + repo 문서 기반 Telegram RAG bot (`src/chatbot/telegram_bot.py`)
- **Pilot-tested (Start-stage)**: Arm 1·2 API-model 파일럿 (`experiments/2026-05-31/`, README Pilot Results) · 로컬 phi-2 smoke (`outputs/runs/smoke_test_*.json`)
- **Scaffolded (Growth-stage)**: DPO+LoRA full training (`src/training/`), 5-arm 정량 benchmark (`src/evaluation/`), LoRA arms 3·4·5 adapter inference
- **TBD**: 최종 벤치마크/평가 지표/프로토콜 (see `docs/benchmark_selection.md`, `docs/decision_log.md`)

## Research questions (from `README.md`, `docs/research_plan.md`)

### RQ1. Preference learning으로 conflict resolution을 내재화할 수 있는가?

- **Concept / definition**
  - `docs/research_plan.md` (Target: context–memory conflict)
  - `docs/experiment_design.md` (comparison arms)
- **Baselines**
  - Base RAG (no training): `configs/experiments/rag_base.yaml`
  - Conflict-Aware Prompting (Start-stage implemented and pilot-tested): `configs/experiments/prompting_conflict_aware.yaml`, `configs/prompts/conflict_aware.md`
- **Preference learning (Growth-stage scaffold)**
  - Training entrypoint: `src/training/train.py`
  - Preference schema: `data/schema/preference_pair.schema.json`
  - LoRA arms configs (scaffold):
    - `configs/experiments/lora_parrag_style.yaml`
    - `configs/experiments/lora_conflict_only.yaml`
    - `configs/experiments/lora_conflict_parrag.yaml`

### RQ2. 어떤 conflict pattern이 학습되고 어떤 것은 한계인가?

- **Conflict scope**
  - In-scope: context–memory conflict (README “연구 범위” / `docs/research_plan.md`)
  - Out-of-scope (main line): inter-context / intra-memory (README / `docs/decision_log.md`)
- **Analysis hooks**
  - Per-run artifacts under `outputs/` and `experiments/` (see `outputs/runs/`, `experiments/2026-05-31/`)
  - Qualitative error analysis template referenced in `docs/experiment_design.md`

### RQ3. Prompting 대비 LoRA 내재화는 얼마나 효과적인가?

- **Design**
  - Prompt-only arm vs. LoRA arms 비교 구도: `docs/experiment_design.md`
- **Implementation touchpoints**
  - Prompting: `configs/prompts/conflict_aware.md` (Start-stage implemented)
  - LoRA: `src/training/train.py` (dry-run scaffold) + LoRA configs (Growth-stage)
- **How to run (today)**
  - 현재는 **Arm 1·2**를 CLI로 확인할 수 있습니다.
    - Base RAG: `make demo`
    - Base RAG vs Conflict-Aware Prompting: `make demo-conflict`
    - 실행 결과 예시: `outputs/runs/smoke_test_base_rag.*`, `outputs/runs/smoke_test_conflict_base.*`, `outputs/runs/smoke_test_conflict_aware.*`
  - LoRA arms(3·5)는 adapter inference·정량 benchmark가 Growth 단계입니다.

### RQ4. Conflict 정렬이 다른 축(informativeness/robustness/citation)을 해치지 않는가?

- **Intended comparison**
  - PA-RAG-style vs conflict-only vs combined arms: `docs/experiment_design.md`
- **Evaluation status**
  - Arm 1·2 파일럿 결과: README · `experiments/2026-05-31/`
  - 5-arm 정량 benchmark / RAGAS protocol: Growth-stage (`src/evaluation/evaluate.py` harness scaffold)

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
- `docs/team_contributions.md` (팀원별 기여 증거)
