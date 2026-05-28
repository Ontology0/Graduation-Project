# Verification Checklist (Repro / Ops)

> 목적: “AI 투명성”을 형식적으로 적는 대신, **사람이 실제로 검증한 항목**을 재현 가능한 형태로 남깁니다.  
> 주의: 스크린샷/로그 공유 시 토큰, 사용자ID, 채팅ID, 파일 경로(개인정보) 등 민감정보를 마스킹합니다.

## A. Repo quick checks (3 minutes)

- [ ] `README.md` 상단에서 `docs/demo.md`, `docs/architecture.md`, `docs/rq_to_implementation_map.md`, `docs/ai_transparency_report.md` 링크를 바로 찾을 수 있다
- [ ] `docs/demo.md`의 smoke test 명령이 현재 코드와 일치한다 (`scripts/run_pipeline.py`)

## B. RAG CLI smoke test (local)

### Command

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

### Pass criteria

- [ ] 콘솔에 `Experiment:` / `Question:` / `Answer:` / `Sources:`가 출력된다
- [ ] `outputs/runs/` 아래 결과 파일이 생성된다(JSON/MD)

## C. Telegram bot safety / ops checks

> Telegram bot은 “프로젝트 공유용” 유틸이며, 운영 안전장치가 핵심입니다. 관련 설명: `docs/telegram_bot_ops.md`

### C1) Allowlist 미설정 시 민감 커맨드 기본 차단

- [ ] `TELEGRAM_REQUIRE_ALLOWLIST=1` 이 켜져있고 `TELEGRAM_ALLOWED_USER_IDS`가 비어있거나 본인이 포함되지 않은 상태에서, 다음 민감 커맨드가 거부된다
  - [ ] `/reindex`
  - [ ] `/save`
  - [ ] `/status` (존재하는 경우)

### C2) 인덱스 재사용 (비용/시간)

- [ ] `configs/experiments/rag_github_bot.yaml`에서 `retrieval.index_dir`가 설정되어 있다
- [ ] 봇을 재시작해도 인덱스를 재사용하며, 매번 문서 전체를 재임베딩하지 않는다
  - 확인 방법(예시): 첫 실행에서 인덱스 생성 로그가 나오고, 재시작 후에는 “load existing index” 경로로 동작하는지 로그로 확인

### C3) Telegram HTML 포맷 렌더링

- [ ] 봇 응답에서 `**bold**`, `` `code` `` 형태가 Telegram에서 기대대로 렌더링된다(HTML parse mode)
  - 확인 방법: 짧은 테스트 질문 1개를 보내고, 굵게/코드 스타일이 적용되는지 눈으로 확인

## D. “정합성” 체크 (문서 ↔ 코드)

- [ ] `docs/architecture.md`의 “Key entrypoints”가 실제 파일 경로와 일치한다
- [ ] `docs/rq_to_implementation_map.md`의 링크들이 끊기지 않는다(파일 존재/경로 일치)
- [ ] `docs/decision_log.md`의 Confirmed/Deferred가 README의 “저장소 상태” 설명과 충돌하지 않는다
