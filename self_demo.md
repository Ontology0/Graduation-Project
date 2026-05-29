# Self-Demo 시연 요령

> **대상:** 이 레포를 처음 보는 평가자 / 팀원 / 외부 방문자  
> **목표:** 로컬에서 5분 안에 RAG 파이프라인이 실제로 동작함을 확인한다.  
> **전제:** Python 3.10+, git 설치 완료

---

## Step 0. 레포 클론 & 환경 설정

```bash
git clone https://github.com/Ontology0/Graduation-Project.git
cd Graduation-Project
pip install -r requirements.txt
```

> API 키가 필요한 경우 `.env.example`을 복사해 `.env`로 만들고 값을 채운다.  
> (Base RAG smoke test는 로컬 HuggingFace 모델로도 동작 — API 키 없이 가능)

```bash
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 등 필요한 키 입력
```

---

## Step 1. Base RAG 파이프라인 실행 (핵심 smoke test)

아래 커맨드 하나로 전체 파이프라인(Load → Chunk → Embed → Retrieve → Generate)을 확인할 수 있다.

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

### 성공 기준

콘솔에 아래 항목이 순서대로 출력되면 정상 동작이다.

```
Experiment: ...
Question:   What is knowledge conflict in RAG?
Answer:     ...
Sources:    ...
```

- `outputs/runs/` 아래 `.json` / `.md` 파일이 생성된다.

---

## Step 2. Knowledge Conflict 시나리오 시연

이 프로젝트의 **핵심 연구 질문**을 직접 체험하는 단계다.

### 시나리오 설명

`data/sample_docs/example_conflict.txt`에는 다음 충돌이 설정되어 있다.

| | 내용 |
|---|---|
| **모델 내부 지식 (parametric)** | Northwood Institute 마스코트 색상 = **deep blue** |
| **검색된 외부 문서 (retrieved)** | 2019 개정판 기준 마스코트 색상 = **silver-green** |

Base RAG는 이 충돌을 감지하지 못하고 잘못된 답을 낼 수 있다.  
Conflict-aware prompting은 외부 문서를 우선하도록 지시한다.

### 실행: Base RAG (충돌 미인식)

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What color is the Northwood Institute mascot?"
```

### 실행: Conflict-Aware Prompting (충돌 인식)

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/prompting_conflict_aware.yaml \
  --docs data/sample_docs/ \
  --question "What color is the Northwood Institute mascot after the 2019 revision?"
```

### 관찰 포인트

- Base RAG 답변이 "deep blue"를 그대로 사용하는가?
- Conflict-aware 답변이 retrieved 문서(silver-green)를 우선하는가?
- 두 답변의 Sources 섹션이 동일한 문서를 참조하는가?

---

## Step 3. 배치 실행 (여러 질문 한 번에)

```bash
python scripts/run_batch.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/
```

결과는 `outputs/runs/` 아래 타임스탬프 폴더에 저장된다.

---

## Step 4. (선택) Telegram RAG 봇 실행

저장소 문서를 지식베이스로 사용하는 챗봇을 로컬에서 실행한다.  
`.env`에 `TELEGRAM_BOT_TOKEN`이 설정되어 있어야 한다.

```bash
python scripts/telegram_bot.py \
  --config configs/experiments/rag_github_bot.yaml \
  --verbose
```

봇에서 사용 가능한 커맨드:
- `/about` — 프로젝트 소개 (README 기반)
- `/run` — 로컬 실행 방법 요약
- `/where <키워드>` — 저장소에서 키워드 위치 찾기
- `/sources` — 최근 답변의 출처 보기

---

## 레포 구조 한눈에 보기

```
src/rag/          ← RAG 파이프라인 (실제 구현)
scripts/          ← CLI 실행 엔트리포인트
configs/          ← 실험 설정(YAML) + 프롬프트(MD)
data/sample_docs/ ← smoke test용 샘플 문서
outputs/          ← 실행 결과 저장 위치
docs/             ← 연구 문서 (architecture, RQ map 등)
```

전체 문서 동선: `README.md` → `docs/architecture.md` → `docs/rq_to_implementation_map.md`

---

## 검증 완료 항목

- [x] `README.md` 충실성: 개요·설치·실행·팀정보·Project Brief 링크 포함
- [x] 필요 파일 존재: `requirements.txt`, `configs/`, `data/sample_docs/`, `src/rag/` 모듈 10개
- [x] 엔트리포인트 실재: `scripts/run_pipeline.py`, `scripts/telegram_bot.py`
- [x] smoke test 커맨드: 위 Step 1 커맨드로 재현 가능
- [ ] 실행 결과물: `outputs/runs/` 커밋 예정 (이슈 [#23](https://github.com/Ontology0/Graduation-Project/issues/23))
- [ ] 데모 영상: 기말 발표 전 업로드 예정 (이슈 [#22](https://github.com/Ontology0/Graduation-Project/issues/22))
