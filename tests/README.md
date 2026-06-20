# tests/

## 목적

레포의 **회귀 테스트** 모음입니다. API 키·GPU·LLM 호출 없이 로컬에서 빠르게 돌릴 수 있는 항목 위주입니다.

`docs/verification_checklist.md` B 섹션에서도 동일하게 `pytest -q` 실행을 권장합니다.

## 실행 방법

```bash
pip install -e ".[dev]"
pytest -q
```

특정 파일만:

```bash
pytest tests/test_prompt_builder.py -q
```

`test_train_dry_run.py`는 training dependency와 mock 기반 dry-run 경로를 확인하는 테스트이므로, 기본 `pytest -q`에서는 `pyproject.toml` 설정에 의해 제외됩니다. 필요 시 명시적으로 실행할 수 있습니다.

```bash
pytest tests/test_train_dry_run.py -q
```

## 파일 설명

| 파일 | 역할 | 상태 |
|------|------|------|
| `test_prompt_builder.py` | Base / conflict-aware prompt template 로딩 및 placeholder 검증 | active |
| `test_schema_files.py` | `data/schema/*.json` JSON 파싱 검증 | active |
| `test_run_batch.py` | pilot JSONL 로드, case → Document 변환, batch output path 검증 | active |
| `test_telegram_format.py` | Telegram HTML escaping / formatting 검증 | active |
| `test_eval_metrics.py` | conflict-resolution accuracy, false-doc follow rate, abstention rate 등 평가 metric 검증 | active |
| `test_preference_schema.py` | preference pair schema와 train/eval JSONL 구조 검증 | active |
| `test_build_preference_pairs.py` | synthetic conflict case → chosen/rejected preference pair 변환 검증 | active |
| `test_train_dry_run.py` | DPO+LoRA dry-run path mock 기반 smoke test | excluded from default pytest by `pyproject.toml` |

---

### `test_prompt_builder.py`

**대상:** `src/rag/prompt_builder.load_prompt_template`

**검증 내용:**
- `configs/prompts/base_rag.md` — system/user 템플릿에 `{retrieved_context}`, `{question}` placeholder 존재
- `configs/prompts/conflict_aware.md` — conflict 관련 system 문구 및 placeholder 존재

**특징:** torch·임베딩·LLM 불필요 (프롬프트 파일 읽기만).

---

### `test_schema_files.py`

**대상:** `data/schema/` 아래 모든 `*.json`

**검증 내용:**
- 각 파일이 유효한 JSON으로 파싱되는지 (`json.load`)

**포함 예:** `conflict_annotation.schema.json`, `preference_pair.schema.json` 등

---

### `test_run_batch.py`

**대상:** `src/rag/pilot_dataset` (batch run용 헬퍼)

**검증 내용:**

| 테스트 | 확인하는 것 |
|--------|-------------|
| `test_load_conflict_dataset_limit` | `pilot_conflicts.jsonl`에서 `limit=2`로 case 로드, 첫 id가 `case_001` |
| `test_documents_from_case` | case → `Document` 리스트 변환, `stance`(outdated/current/distractor) 메타데이터 |
| `test_output_path` | `batch_output_path()`가 `outputs/<experiment>/pilot_conflicts_*.jsonl` 형태 경로 생성 |

**데이터:** `data/synthetic_conflicts/pilot_conflicts.jsonl` (레포에 포함된 pilot 파일 필요)

---

### `test_eval_metrics.py`

**대상:** `src/evaluation/evaluate.py` metric helpers

**검증 내용:** `contains_target`, conflict-resolution accuracy, false-doc follow rate, abstention rate, case-type aggregation

---

### `test_preference_schema.py` / `test_build_preference_pairs.py`

**대상:** `data/synthetic_conflicts/build_preference_pairs.py`, preference JSONL schema

**검증 내용:** train/eval split 필터, stance→role 매핑, chosen/rejected pair 생성

---

### `test_train_dry_run.py`

**대상:** `src/training/train.py` dry-run 경로 (mock 기반)

**특징:** 기본 `pytest -q`에서 제외 (`pyproject.toml` → `addopts = "--ignore=tests/test_train_dry_run.py"`). heavy ML dependency 없이 scaffold 경로만 확인.

---

## 현재 범위 밖

아래 항목은 아직 **end-to-end** 테스트가 없습니다.

- Full end-to-end RAG pipeline with real model download / API call
- Live Telegram bot execution with real bot token and network
- Full-scale DPO+LoRA training on Llama 3.1-8B
- Adapter-based inference for LoRA arms
- Large benchmark evaluation across all five arms

현재 테스트는 API 키·GPU 없이 빠르게 검증 가능한 **unit test**와 **scaffold smoke test**에 초점을 둡니다.

추가 테스트는 `src/rag/pipeline.py` 등 실제 entrypoint를 확장할 때 같은 패턴으로 `test_*.py`를 추가하면 됩니다.
