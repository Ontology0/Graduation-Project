## Telegram 프로젝트 공유용 RAG 봇 운영/비용 노트

### 이 봇이 “매번 비용이 발생”하나?

부분적으로만 맞습니다.

- **문서 인덱싱(임베딩) 비용**: `retrieval.index_dir`가 설정되어 있으면(현재 `outputs/index/github_kb`) 인덱스를 디스크에 저장해두고 재사용하므로, **매 질문마다 문서 전체를 다시 임베딩하지 않습니다.**  
  다만 인덱스가 없거나(`index_dir` 미설정/삭제), 문서 범위를 바꿔서 재인덱싱하면 그때는 **문서 청크 임베딩 비용이 한 번** 발생합니다.
- **질문(쿼리) 당 비용**: 질문을 받을 때마다
  - **쿼리 임베딩**(예: `openai/text-embedding-3-small`)
  - **LLM 생성 호출**(예: Anthropic Claude)
  이 두 비용은 **매 질문마다** 발생합니다.

### 왜 서버에 “상시 탑재”하면 좋아지나?

- **인덱스 재사용 안정화**: 서버(또는 라즈베리파이/VPS)에 `outputs/index/...`를 유지하면 재시작해도 인덱스를 그대로 로드해서, “부팅할 때마다 재인덱싱” 같은 실수를 줄입니다.
- **운영/보안 통제**: 단일 인스턴스로 운영하면서
  - allowlist(허용 사용자/채팅) 강제
  - 그룹 차단
  - 레이트리밋
  - 키 사용량 한도
  같은 통제를 한 곳에서 일관되게 적용할 수 있습니다.

### 설정 포인트(현재 기본값)

- **인덱스 저장 경로**: `configs/experiments/rag_github_bot.yaml`의 `retrieval.index_dir`
- **문서 범위**: 텔레그램 봇 부트 시 `RepoKBConfig(include_dirs=("docs",), include_files=("README.md","CLAUDE.md"))`
- **쿼리/문서 임베딩 모델**: `retrieval.embedding_model`
- **생성 모델**: `llm.provider`, `llm.model`

### 운영 플로우(딱 이거만)

- **문서 수정/추가**: `README.md` / `docs/**` / `CLAUDE.md`
- **봇에서 갱신**: 텔레그램에서 `/reindex`
- **끝**: 이후 질문부터는 새 인덱스 기준으로 검색됨

### 주의 2개(비용/보안)

- **비용**: `/reindex` 때만 “문서 청크 임베딩 비용”이 크게 한 번 나가고, 평소엔 “질문 임베딩 + Claude 생성”만 나감.
- **보안**: `/reindex`는 “민감 커맨드”라 allowlist가 켜져있을 때만 쓰게 두는 걸 권장.  
  예: `TELEGRAM_REQUIRE_ALLOWLIST=1` + `TELEGRAM_ALLOWED_USER_IDS=...` (+ 선택: `TELEGRAM_ALLOWED_CHAT_IDS=...`)

### 보안 권장(키 도난/과금 방지)

- **봇 전용 API 키를 따로 발급**하고 사용량 한도를 낮게 걸기(OpenAI/Anthropic 콘솔에서 hard limit 권장)
- **화이트리스트 강제 + 그룹 차단**:
  - `TELEGRAM_REQUIRE_ALLOWLIST=1`
  - `TELEGRAM_ALLOWED_USER_IDS=...`
  - (선택) `TELEGRAM_ALLOWED_CHAT_IDS=...`
  - `TELEGRAM_ALLOW_GROUPS=0`

