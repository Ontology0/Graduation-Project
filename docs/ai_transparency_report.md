# AI 투명성 리포트

> 본 문서는 프로젝트 개발 과정에서 AI 도구를 활용한 내역을 투명하게 기록합니다.
> 각 작업에 대해 AI가 수행한 범위, 인간이 검증·판단한 범위를 명시합니다.

---

## 1. 단계별 AI 활용 현황

### 1.1 선행 연구 분석

| 항목 | 내용 |
|------|------|
| **사용 도구** | Claude 3.5 Sonnet, NotebookLM |
| **활용 내용** | PA-RAG, DPA-RAG, ClashEval 등 관련 논문 분석 및 핵심 방법론 정리 (DPO, LoRA, RAFT 등). 벤치마크 구조 정리 및 질의 |
| **인간 검증** | NotebookLM 폐쇄형 설정으로 외부 데이터 혼입 방지. 원문 논문과 수식·수치 대조 확인 |

### 1.2 프로젝트 구조 설계 및 리팩토링

| 항목 | 내용 |
|------|------|
| **사용 도구** | Cursor (Claude Opus 4.6) |
| **활용 내용** | 기존 scaffold 구조를 ML 연구 레포지토리 관례에 맞게 전면 리팩토링. 아래 세부 내역 참조 |
| **인간 판단** | 리팩토링 방향 (src/ 레이아웃, 수업 제출물 분리, 폴더 네이밍) 확인 및 승인. GitHub Pages 유지 여부, 수업 자료 처리 방식 결정 |

**세부 변경 내역:**

| 변경 사항 | AI 수행 | 인간 판단 |
|-----------|---------|-----------|
| `rag/`, `finetuning/`, `eval/` → `src/` 하위로 통합 | 파일 이동, import 경로 수정, 커밋 생성 | 구조 방향 승인 |
| `prompts/` → `configs/prompts/` 이동 | 파일 이동 및 YAML 참조 경로 수정 | 프롬프트를 config 하위로 둘지 결정 |
| `configs/*.yaml` → `configs/experiments/` 정리 | 디렉토리 구조화 | 네이밍 승인 |
| `docs/submission_materials/` → `course/` 분리 | 파일 이동 | 수업 제출물 유지 + 분리 결정 |
| `self_demo.md` → `docs/demo.md` 이동 | 파일 이동 | - |
| `results/` → `outputs/` 이름 변경 | 디렉토리 rename | - |
| `pyproject.toml` 추가 | 파일 생성 (패키지 메타데이터, pytest 설정) | - |
| `scripts/`, `tests/` 디렉토리 추가 | 디렉토리 및 CLI 스크립트 생성 | - |
| `.DS_Store` git 추적 해제 | `git rm --cached` 실행 | - |
| `pipeline_stub.py` 삭제 | 실제 pipeline.py로 대체 후 삭제 | - |
| README.md, CLAUDE.md 경로 전체 업데이트 | 파일 참조 경로 일괄 수정 | 최종 내용 확인 |

**관련 커밋:** `4296c12` ~ `0de275c` (13개 커밋)

### 1.3 RAG 파이프라인 구현

| 항목 | 내용 |
|------|------|
| **사용 도구** | Cursor (Claude Opus 4.6) |
| **활용 내용** | RAG 파이프라인의 모듈별 코드 생성. 아래 세부 내역 참조 |
| **인간 판단** | 구현 범위 및 모듈 분할 방식 결정. 모델 선택 (phi-2, all-MiniLM-L6-v2), FAISS 백엔드 채택 |

**세부 구현 내역:**

| 모듈 | AI 생성 내용 | 인간 판단 |
|------|-------------|-----------|
| `config.py` | YAML 설정 로더 + `.env` 로딩 | - |
| `document_loader.py` | txt/json/jsonl 포맷 문서 로딩, Document 데이터클래스 | - |
| `chunker.py` | 문장 경계 인식 텍스트 청킹 (overlap 지원) | chunk_size, overlap 값 |
| `embedder.py` | sentence-transformers 래퍼, L2 정규화 임베딩 | 모델 선택 |
| `vector_store.py` | FAISS IndexFlatIP 래퍼, 저장/로드 지원 | 백엔드 선택 |
| `retriever.py` | Embedder + VectorStore 결합 검색 | top_k 설정 |
| `prompt_builder.py` | base/conflict-aware 프롬프트 빌더, chat template 형식 | 프롬프트 내용 검토 |
| `generator.py` | HuggingFace AutoModelForCausalLM 래퍼 | 모델 선택 |
| `pipeline.py` | 전체 파이프라인 오케스트레이션 + CLI | 파이프라인 구조 승인 |

**관련 커밋:** `f9cff2f` ~ `6ce882a` (12개 커밋)

### 1.4 데이터 구성 (예정)

| 항목 | 내용 |
|------|------|
| **사용 도구** | ChatGPT-3.5 (예정) |
| **활용 내용** | RAG-aware preference 데이터 자동 생성. chosen/rejected 쌍 생성으로 비용 효율성 확보 |
| **인간 검증** | 데이터 샘플링 통한 품질, 정합성 검수 필수 |

### 1.5 실험 설계 및 평가 (예정)

| 항목 | 내용 |
|------|------|
| **사용 도구** | GPT-4o, Gemini 1.5 Pro (예정) |
| **활용 내용** | Baseline vs Hybrid 대조군 설정 자문. Faithfulness Score 등 주관적 지표 평가. LLM-as-a-judge 방식 도입 |
| **인간 검증** | RAGAS 지표와 병행 교차 검증 (RTX 3090 x 4 환경 고려) |

---

## 2. 인간 주도 핵심 연구 영역

연구의 독창성과 신뢰성을 담보하기 위해 다음 영역은 AI의 보조 없이 연구진이 직접 수행합니다.

- **연구 주제 및 가설 설정**: Knowledge Conflict를 PA-RAG 확장 축으로 삼는 연구 방향, 4개 RQ 설정
- **DPO 학습 데이터 품질 검토**: AI가 생성한 선호도 데이터 쌍을 직접 샘플링하여 연구 목적과의 정합성 및 편향 여부를 직접 판단
- **핵심 가설 및 로직 설계**: 지식 충돌 시나리오에서 외부 근거 vs 내부 지식 우선순위를 DPO로 내재화하는 방법론 고안
- **최종 의사결정**: AI가 제시한 다양한 선택지 중 최적의 방법론을 채택하고, 도출된 데이터에 대한 의미론적 분석을 수행
- **결과 검증**: AI가 요약·정리한 모든 내용과 실제 논문의 수식, 수치 데이터를 대조하여 정확성 최종 확인

---

## 3. AI 활용 원칙 및 윤리

- **교차 검증 원칙**: AI 도구의 답변을 무비판적으로 수용하지 않으며, 모든 기술적 인용구와 수치는 원문 논문을 직접 대조하여 검증
- **데이터 보안**: NotebookLM 등 활용 시 개인정보나 비공개 데이터는 업로드하지 않으며, 모든 처리는 연구용 공개 벤치마크 데이터셋에 한정
- **코드 검토**: AI가 생성한 코드는 팀원이 리뷰하고, 핵심 로직(DPO loss, conflict resolution 규칙 등)은 논문 수식과 대조 검증
- **투명성**: AI가 관여한 모든 작업은 본 문서에 기록하며, 커밋 로그를 통해 AI 생성 코드와 인간 작성 코드를 추적 가능하게 유지

---

## 4. AI 활용 도구 요약

| 도구 | 용도 | 활용 단계 |
|------|------|-----------|
| **Cursor (Claude Opus 4.6)** | 코드 생성, 리팩토링, 커밋 관리 | 구현, 구조 설계 |
| **Claude 3.5 Sonnet** | 논문 분석, 방법론 정리 | 선행 연구 |
| **NotebookLM** | 논문 기반 폐쇄형 질의응답 | 선행 연구 |
| **ChatGPT-3.5** | preference 데이터 생성 (예정) | 데이터 구성 |
| **GPT-4o** | 실험 설계 자문, LLM-as-a-judge (예정) | 실험 및 평가 |
| **Gemini 1.5 Pro** | 평가 교차 검증 (예정) | 실험 및 평가 |

---

<div align="center">
<sub>최종 업데이트: 2026-05-28</sub>
</div>

---

## 1.6 Telegram 프로젝트 공유용 RAG 봇 개발/운영 개선

| 항목 | 내용 |
|------|------|
| **사용 도구** | Cursor (GPT-5 계열) |
| **활용 내용** | Telegram 봇 코드 정리(폴더 구조), 텍스트 출력 UX 개선(텔레그램 포맷), 응답 끊김 완화, 운영 보안(allowlist/그룹 차단/레이트리밋) 강화, 운영 문서화 및 커맨드 UX 추가 |
| **인간 판단** | 봇을 저장소 공유/온보딩 용도로 유지할지, 공개 범위(allowlist 강제/민감 커맨드 기본 잠금), 모델/임베딩 비용-품질 트레이드오프 선택, README vs docs 문서 위치 결정, “서버리스 운영 시 수동 `/reindex`” 운영 방침 확정 |

**재현 가능한 검증 절차(별도 문서):** `docs/verification_checklist.md`

**세부 변경 내역:**

| 변경 사항 | AI 수행 | 인간 판단 |
|-----------|---------|-----------|
| Telegram 봇 코드 위치 명확화 | `src/chatbot/telegram_bot.py`로 로직 이동, `scripts/telegram_bot.py`를 얇은 엔트리포인트로 정리 | “챗봇은 챗봇 폴더로” 구조 요구 승인 |
| README 갱신 | `README.md`에 `src/chatbot/` 반영, `configs/` 역할 설명 추가, “Telegram 프로젝트 공유용 RAG 봇” 섹션 추가(봇 이름/초대 링크 제외) | README에 포함할 범위/표현 톤 결정 |
| 봇 기능 설명 커맨드 | `/what`(alias `/intro`) 커맨드 추가로 “이 봇이 RAG로 동작하는 구조”를 고정 문구로 안내 | 사용자가 봇을 테스트/공유할 때 반복 질문을 줄이기 위한 UX 요구 승인 |
| 텔레그램 포맷 대응 | `**bold**`, `` `code` ``를 Telegram HTML(`<b>`, `<code>`)로 변환하여 전송 (`ParseMode.HTML`) | “텔레그램에서는 **가 아님” UX 요구 승인 |
| 응답 끊김 완화 | 문장 미완성으로 끝나면 “짧게 재생성” 대신 “이어쓰기(continue)”로 1~3문장만 보강 | “재생성 구림” 피드백 반영 |
| 전송 안정화 | 다중 메시지 전송 중 rate-limit 발생 시 대기 후 재전송(재시도) | 운영 안정성 우선 |
| 접근 제어 강화 | allowlist/그룹 차단/채팅 제한 옵션 추가 + **민감 커맨드(`/reindex`, `/save`, `/status`)는 allowlist 없으면 기본 거부**로 잠금 | 키 도난/과금 리스크를 “설정 실수”까지 포함해 방지하도록 정책 확정 |
| 운영 문서화 | `docs/telegram_bot_ops.md`에 서버리스 운영 플로우(문서 변경 → `/reindex`) 및 비용/보안 주의사항을 명시, `docs/decision_log.md`에 기록 | README에는 개요만 유지하고 운영 디테일은 docs로 분리한다는 방침 확정 |

**검증/점검(인간 수행):**
- Telegram 봇 실행 및 주요 커맨드 플로우(`/start`, `/what`, `/reindex`) 동작 확인
- 보안 정책 확인: allowlist 미설정 시 민감 커맨드가 거부되는지, 그룹 차단/채팅 제한 옵션이 기대대로 작동하는지 점검
- 비용 구조 점검: `retrieval.index_dir` 기반 인덱스 재사용 여부 확인 및 “문서 재인덱싱 비용 vs 질문당 비용” 구분을 문서화

**관련 파일:**
- `src/chatbot/telegram_bot.py`
- `scripts/telegram_bot.py`
- `README.md`
- `docs/telegram_bot_ops.md`
- `docs/decision_log.md`
- `configs/experiments/rag_github_bot.yaml`
