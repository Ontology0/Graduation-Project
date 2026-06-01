# src/chatbot/

**Telegram RAG 봇** 구현 모듈입니다. repo를 지식베이스로 `src/rag` 파이프라인에 연결해 질의·명령을 처리합니다. CLI 진입점은 `scripts/telegram_bot.py`(thin wrapper)입니다.

## 파일별 역할

| 파일 | 역할 |
|------|------|
| `telegram_bot.py` | 봇 앱 — 명령·메시지 핸들러, allowlist·rate limit, `RAGPipeline` 연동 |
| `telegram_format.py` | Telegram HTML(`parse_mode`)용 Markdown 변환·출처 표시 포맷 |

## 실행

```bash
python scripts/telegram_bot.py --config configs/experiments/rag_github_bot.yaml
```

`.env`에 `TELEGRAM_BOT_TOKEN` 등 필요. 설정 예: `configs/experiments/rag_github_bot.yaml`

## 상태

**구현됨:** 일반 질의 RAG, `/where`, `/status` 등. `/reindex`, `/save` 등 민감 명령은 allowlist 필요.

**운영·보안:** `docs/telegram_bot_ops.md`
