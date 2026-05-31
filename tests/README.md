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

## 파일 설명

| 파일 | 역할 |
|------|------|
| `__init__.py` | `tests` 패키지 마커 (내용 없음). pytest가 `tests/`를 테스트 루트로 인식하는 데 사용 |
| `test_prompt_builder.py` | `configs/prompts/*.md` 프롬프트 템플릿 로딩 검증 |
| `test_schema_files.py` | `data/schema/*.json` JSON Schema 파일 파싱 가능 여부 검증 |
| `test_run_batch.py` | pilot JSONL 로드·`Document` 변환·batch 출력 경로 헬퍼 검증 |

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

## 현재 범위 밖

아래는 **아직** 이 디렉터리에 테스트가 없습니다.

- end-to-end RAG pipeline (`scripts/run_pipeline.py`) — API 키·모델 다운로드 필요
- Telegram bot (`src/chatbot/telegram_bot.py`) — 봇 토큰·네트워크 필요
- DPO 학습 / 평가 scaffold (`src/training/`, `src/evaluation/`)

추가 테스트는 `src/rag/pipeline.py` 등 실제 entrypoint를 확장할 때 같은 패턴으로 `test_*.py`를 추가하면 됩니다.
