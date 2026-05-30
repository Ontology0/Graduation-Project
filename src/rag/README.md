# src/rag/

## 목적

본 프로젝트의 RAG baseline 파이프라인입니다. 텍스트를 ingest하고 retriever를 구성한 뒤, 검색된 context를 prompt에 넣어 답변을 생성합니다.

**로컬 HuggingFace 모델**(기본 smoke test 경로)과 **API 백엔드**(Telegram 봇 설정: OpenAI embedding + Anthropic generation)를 모두 지원합니다. conflict-aware prompt 템플릿은 `configs/prompts/`에 있으며, YAML의 `prompt_file`로 불러옵니다.

## 아키텍처

```text
documents ─→ document_loader ─→ chunker ─→ embedder ─→ vector_store ──┐
                     │                              ↑ save/load index │
                     │                              │ (retrieval.index_dir)
query ─→ retriever (embed + search) ─→ prompt_builder ─→ generator ─→ RAGResult
                                                                          │
                                                                          └─→ reporting → outputs/runs/
```

**오케스트레이션:** `pipeline.py`의 `RAGPipeline`이 위 단계를 연결합니다. `RAGResult`에는 답변, 검색 출처, (선택) 생성 메타데이터가 담깁니다.

## 모듈

| 모듈 | 설명 |
|------|------|
| `config.py` | YAML 실험 설정 로드, repo 기준 경로 해석, `.env` 시크릿 읽기 |
| `document_loader.py` | `.txt`, `.md`, `.json`, `.jsonl` → `Document` 객체 |
| `chunker.py` | 문장 경계를 고려한 overlapping chunk 분할 |
| `embedder.py` | **SentenceTransformers**(로컬) 또는 **OpenAI API**(`openai/...` 접두사) 임베딩 |
| `vector_store.py` | **FAISS** vector store(기본) + **NumPy fallback**; 디스크 save/load |
| `retriever.py` | 쿼리 임베딩 + vector store top-k 검색 |
| `prompt_builder.py` | `configs/prompts/*.md` 또는 내장 base / conflict-aware 템플릿으로 chat-style prompt 구성 |
| `generator.py` | **HuggingFace causal LM**(`Generator`) 또는 **Anthropic Messages API**(`AnthropicGenerator`) |
| `pipeline.py` | end-to-end 오케스트레이터: index, query, (선택) index 영속화 |
| `reporting.py` | 실행 결과를 `outputs/runs/`에 JSON + Markdown으로 저장 |
| `github_kb.py` | Telegram RAG 봇용 repo 공개 문서(`README.md`, `docs/` 등) 로드 |
| `pilot_dataset.py` | batch run용 synthetic conflict pilot case(JSONL) 로드 |

## 설정

실험 설정은 `configs/experiments/*.yaml`에 정의합니다. 자주 쓰는 키:

| 항목 | 역할 |
|------|------|
| `experiment_name` | `RAGResult.config_name`에 저장되는 실험 라벨 |
| `llm.provider` / `llm.model` | `hf`(기본) 또는 `anthropic` / `claude` |
| `retrieval.embedding_model` | 예: `sentence-transformers/all-MiniLM-L6-v2`, `openai/text-embedding-3-small` |
| `retrieval.backend` | `faiss` 또는 `numpy` |
| `retrieval.index_dir` | (선택) 디스크 index 경로 — 재시작 시 재사용 |
| `prompt_file` | `configs/prompts/` 아래 Markdown prompt 템플릿 |
| `generation` | `max_new_tokens`, `temperature` 등 |

대표 config 예시:

- **Base RAG (로컬 HF):** `configs/experiments/rag_base.yaml`
- **Conflict-aware prompting:** `configs/experiments/prompting_conflict_aware.yaml`
- **Telegram bot (API):** `configs/experiments/rag_github_bot.yaml`

## 진입점

| 스크립트 | `src/rag/` 사용 방식 |
|----------|----------------------|
| `scripts/run_pipeline.py` | 단일 질문 CLI smoke test |
| `scripts/run_batch.py` | JSONL pilot dataset batch run → `outputs/` |
| `scripts/telegram_bot.py` | `github_kb.load_repo_documents` + `RAGPipeline` |

추가 설명: `docs/architecture.md`, `docs/demo.md`

## 빠른 시작

**단일 질문 (로컬 HF; 최초 실행 시 모델 다운로드 필요):**

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

**pilot case batch (JSONL dataset 준비된 경우):**

```bash
python scripts/run_batch.py \
  --config configs/experiments/rag_base.yaml \
  --dataset data/synthetic_conflicts/pilot_conflicts.jsonl \
  --limit 5
```

성공 기준·출력 경로: `docs/demo.md`

## 현재 상태

`src/rag/`는 **1차 동작 초안**(load → chunk → embed → retrieve → generate → report)입니다. **벤치마크 검증은 아직 없으며**, 최종 eval 점수는 보고하지 않습니다.

**구현됨**

- YAML 기반 pipeline + index save/load
- base / conflict-aware prompt 로드
- 로컬 HF 및 API(OpenAI embed / Anthropic generate) 백엔드
- `outputs/runs/` 실행 결과 저장
- repo KB loader, pilot JSONL batch helper

**남은 작업**

- 벤치마크·dataset 선정 (`docs/benchmark_selection.md`)
- 평가 지표·프로토콜 (`src/evaluation/`, `docs/experiment_design.md`)
- fine-tuned variant용 LoRA adapter 로드 (`configs/experiments/lora_*.yaml`는 scaffold)
