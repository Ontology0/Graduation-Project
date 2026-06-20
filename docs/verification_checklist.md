# Verification Checklist (Repro / Ops)

> **목적:** “AI 투명성”을 형식적으로 적는 대신, **사람이 실제로 검증한 항목**을 재현 가능한 형태로 남깁니다.  
> **사용법:** 섹션별로 실행 → Pass criteria 체크 → 아래 **검증 기록**에 날짜·환경·관찰(로그 한 줄·스크린샷 경로)을 적습니다.  
> **주의:** 스크린샷·로그 공유 시 토큰, 사용자 ID, 채팅 ID, 개인 경로 등 민감정보를 마스킹합니다.

## 검증 기록 (템플릿)

| 항목 | 검증일 | 검증자 | 환경 (OS / Python) | 결과 | Evidence (로그·경로·PR) |
|------|--------|--------|---------------------|------|-------------------------|
| B. pytest | 2026-05-31 | 박세령 | macOS 24.6 / Python 3.12 | Pass | `6 passed in 0.11s` |
| B. pytest | 2026-06-20 | 박세령 | macOS 24.6 / Python 3.12 | Pass | `25 passed in 0.19s`, `test_train_dry_run.py` ignored by pyproject config |
| C. RAG CLI | 2026-05-31 | bbberylll | Windows / 3.x | Pass | `outputs/runs/20260531T104426Z.json` |
| C. RAG CLI smoke test | 2026-05-31 | 박세령 | macOS 24.6 / Python 3.12, phi-2 MPS | Pass | `outputs/runs/smoke_test_base_rag.json` |
| C. Conflict 시나리오 (base) | 2026-05-31 | 박세령 | macOS 24.6 / Python 3.12, phi-2 MPS | Pass | `outputs/runs/smoke_test_conflict_base.json` |
| C. Conflict 시나리오 (conflict-aware) | 2026-05-31 | 박세령 | macOS 24.6 / Python 3.12, phi-2 MPS | Pass | `outputs/runs/smoke_test_conflict_aware.json` |
| D0. 설정 파일 정적 | 2026-05-31 | 박세령 | 코드 리뷰 | Pass | `rag_github_bot.yaml` index_dir 확인, `.env.example` 토큰 키 확인 |
| D1. allowlist 가드 | 2026-05-31 | 박세령 | 코드 리뷰 (`telegram_bot.py` L230-238) | Pass (코드) | `sensitive=True` → allowlist 없으면 "접근 불가" 거부 확인 |
| D4. HTML 포맷 | 2026-05-31 | 박세령 | 코드 리뷰 (`telegram_bot.py` L67-97) | Pass (코드) | `_html_escape` + `ParseMode.HTML` 전체 적용 확인 |
| D1. 일반질문 대조 (live) | 2026-05-31 | 박세령 | @alltology_rag_bot (Railway) | Pass | "대한민국 대통령" 질문 → 범위 밖 안내, 거부 아님 |
| D4. HTML 포맷 (live) | 2026-05-31 | 박세령 | @alltology_rag_bot (Railway) | Pass | `/where` 응답에서 code·bold 스타일 렌더링 확인 |
| C4. Railway 연결 | 2026-05-31 | 박세령 | @alltology_rag_bot (Railway) | Pass | 봇 응답 확인 |

## 사전 준비

| 필요 항목 | A 정적 | B pytest | C RAG CLI | D Telegram |
|-----------|:------:|:--------:|:---------:|:----------:|
| 레포 clone | ✓ | ✓ | ✓ | ✓ |
| `pip install -r requirements.txt` | | ✓ | ✓ | ✓ |
| `.env` (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) | | | ✓ | ✓ |
| `TELEGRAM_BOT_TOKEN` | | | | ✓ |
| 네트워크 (임베딩·LLM API) | | | ✓ | ✓ |

관련 문서: [demo.md](demo.md) · [architecture.md](architecture.md) · [telegram_bot_ops.md](telegram_bot_ops.md) · [rq_to_implementation_map.md](rq_to_implementation_map.md)

---

## A. Repo quick checks (~3분, API 불필요)

README·docs 진입점과 smoke 명령이 **현재 코드와 같은지** 빠르게 확인합니다.

- [ ] `README.md` 상단에서 아래 문서 링크를 바로 찾을 수 있다
  - [ ] `docs/demo.md`
  - [ ] `docs/architecture.md`
  - [ ] `docs/rq_to_implementation_map.md`
  - [ ] `docs/ai_transparency_report.md`
  - [ ] `docs/verification_checklist.md` (본 문서)
- [ ] `docs/demo.md`의 smoke test 명령이 `scripts/run_pipeline.py` 인자와 일치한다
- [ ] `configs/experiments/rag_base.yaml`, `configs/experiments/rag_github_bot.yaml` 파일이 존재한다
- [ ] `data/sample_docs/`에 smoke용 샘플 문서가 있다

**빠른 확인 (선택):**

```bash
test -f scripts/run_pipeline.py && test -f configs/experiments/rag_base.yaml && echo "entrypoints OK"
```

---

## B. Unit tests (~1분, API 불필요)

로컬에서 API 키 없이 돌아가는 회귀 테스트입니다.

### Command

```bash
pip install -e ".[dev]"
pytest -q
```

### Pass criteria

- [x] API 키 없이 실행 가능한 기본 pytest suite가 통과한다. 최신 실행 결과는 아래 **검증 기록**에 날짜별로 추가한다.
- [x] `tests/test_prompt_builder.py`, `tests/test_schema_files.py`, `tests/test_run_batch.py` 등 기본 suite 통과 — **25 passed in 0.19s** (2026-06-20, `test_train_dry_run.py` 제외)
- [x] 실패 시: 실패 테스트 이름과 traceback 첫 줄을 검증 기록에 남긴다 — 실패 없음

---

## C. RAG CLI smoke test (local, API 필요)

[docs/demo.md](demo.md)와 동일한 최소 재현 경로입니다.

### Preflight

- [x] `.env` 또는 환경 변수에 `ANTHROPIC_API_KEY`가 설정되어 있다 (HF 모델 사용 시 불필요)
- [x] `outputs/runs/` 디렉터리가 없으면 자동 생성되는지 확인 → 자동 생성 확인

> 메모: 로컬 phi-2 실행은 외부 API 키 불필요. `.env` 항목은 LLM API 백엔드 사용 시에만 해당.

### Command

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

### Pass criteria

- [x] 종료 코드가 0이다 (에러 traceback 없음)
- [x] 콘솔에 `Experiment:` / `Question:` / `Answer:` / `Sources:`가 출력된다
- [x] `Saved run:` 아래 JSON·MD 경로가 출력된다
- [x] 출력된 경로에 실제 파일이 생성된다 (`outputs/runs/<stem>.json`, `.md`)
- [x] JSON에 `question`, `predicted_answer`, `retrieved_sources` 필드가 포함된다

**실패 시 점검:** API 키·요금 한도 · `requirements.txt` 설치 · `--verbose`로 임베딩/LLM 단계 로그 확인

---

## D. Telegram bot safety / ops (API + 봇 토큰 필요)

Telegram 봇은 프로젝트 공유용 유틸입니다. **운영 안전장치**가 핵심입니다. 상세: [telegram_bot_ops.md](telegram_bot_ops.md)

**진입점:** `scripts/telegram_bot.py` → `src/chatbot/telegram_bot.py`  
**설정:** `configs/experiments/rag_github_bot.yaml` (`retrieval.index_dir: outputs/index/github_kb`)

### D0) 설정 파일 (정적)

- [x] `configs/experiments/rag_github_bot.yaml`에 `retrieval.index_dir`가 설정되어 있다 (`outputs/index/github_kb`)
- [x] `.env.example`에 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS` 등이 문서화되어 있다

### D1) 민감 커맨드 — allowlist 없으면 기본 거부

코드상 `/reindex`, `/save`, `/status`는 **`TELEGRAM_ALLOWED_USER_IDS`와 `TELEGRAM_ALLOWED_CHAT_IDS`가 모두 비어 있으면** 거부됩니다 (`sensitive=True` 가드).  
`TELEGRAM_REQUIRE_ALLOWLIST`와 **별개**로 동작합니다.

**테스트 조건:** allowlist 미설정(또는 본인 ID 미포함) 상태에서 봇에 아래 커맨드 전송

- [x] `/reindex` → `접근 불가. (민감 커맨드는 화이트리스트 설정 필요)` — 코드 확인 (`telegram_bot.py` L234-238, `sensitive=True` 가드)
- [x] `/save` → 동일하게 거부 — 코드 확인 (L325, `sensitive=True`)
- [x] `/status` → 동일하게 거부 — 코드 확인 (L425, `sensitive=True`)
- [x] (대조) 일반 텍스트 질문은 거부 아님 — 범위 밖 질문("대한민국 대통령") 시 안내 메시지로 정상 처리 확인 (2026-05-31 live)

### D2) 전체 잠금 — `TELEGRAM_REQUIRE_ALLOWLIST=1`

운영·스테이징에서 권장하는 강화 옵션입니다.

- [ ] `TELEGRAM_REQUIRE_ALLOWLIST=1`이고 allowlist가 비어 있으면, **일반 질문 포함** 모든 접근이 `접근 불가. (화이트리스트/채팅 제한)`으로 거부된다
- [ ] allowlist에 본인 ID를 넣으면 `/start` 및 일반 질문이 다시 동작한다

### D3) 인덱스 재사용 (비용·시간)

- [ ] **첫 기동** (인덱스 폴더 없음): 임베딩·인덱싱 로그가 나오고 `outputs/index/github_kb/` 아래 파일이 생성된다
- [ ] **재기동** (인덱스 폴더 유지): 로그에 `Loaded index from outputs/index/github_kb` (또는 설정 경로)가 보이고, 전체 문서 재임베딩 없이 질문에 답한다
- [ ] `/reindex` 실행 후에만 문서 청크 임베딩 비용이 다시 발생한다 (평소는 질문 임베딩 + LLM 생성만)

### D4) Telegram HTML 포맷

- [x] 봇 응답에서 `**굵게**`, `` `코드` `` 마크다운이 Telegram HTML로 기대대로 렌더링된다 — 코드 확인 (`telegram_bot.py` L67-97, `_html_escape` + `ParseMode.HTML`)
- [x] 파일 경로·커밋 해시 등이 `<`, `>` 등 특수문자 포함 시 깨지지 않는다 — `html.escape` 선처리 후 태그 주입 방식 확인

### D5) 레이트리밋 (선택)

- [ ] `TELEGRAM_RATE_LIMIT_PER_MIN`을 낮게 두고 연속 요청 시 `요청이 너무 많아` 메시지가 나온다

---

## E. 문서 ↔ 코드 정합성 (~5분, API 불필요)

문서가 **과장·유령 경로** 없이 현재 레포 상태를 반영하는지 확인합니다.

- [ ] `docs/architecture.md`의 Key entrypoints가 실제 파일과 일치한다
  - `scripts/run_pipeline.py`, `src/rag/pipeline.py`, `scripts/telegram_bot.py`, `src/chatbot/telegram_bot.py`
- [ ] `docs/rq_to_implementation_map.md`의 링크·경로가 끊기지 않는다
- [ ] `docs/decision_log.md`의 Confirmed/Deferred가 README **저장소 상태**와 충돌하지 않는다
- [ ] README의 데모 링크(HuggingFace Spaces, 텔레그램 봇 등)가 의도한 대상을 가리킨다 (404·만료 여부)
- [ ] `docs/demo.md`의 “측정되지 않은 결과”·scaffold 표현이 README·`ai_transparency_report.md`와 모순되지 않는다

**빠른 링크 점검 (선택):**

```bash
# architecture에 적힌 entrypoint 존재 확인
for f in scripts/run_pipeline.py src/rag/pipeline.py scripts/telegram_bot.py src/chatbot/telegram_bot.py; do
  test -f "$f" && echo "OK $f" || echo "MISSING $f"
done
```

---

## F. 제출·데모 전 최종 확인 (체크리스트)

기말 발표·외부 공유 직전에 한 번 더 훑습니다.

- [ ] C 섹션 smoke test를 **깨끗한 venv**에서 재현했다
- [ ] D 섹션 민감 커맨드 거부를 **운영 `.env` 설정** 기준으로 확인했다
- [ ] 검증 기록 표에 Pass/Fail과 evidence를 남겼다
- [ ] 공유용 스크린샷·로그에서 API 키·토큰·개인 ID를 마스킹했다
- [ ] 아직 없는 벤치마크 점수·RAGAS 수치를 README·슬라이드에 **주장하지 않았다** (scaffold 단계)
