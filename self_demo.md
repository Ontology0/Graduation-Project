# Self-Demo 시연 요령

> **대상:** 이 레포를 처음 보는 평가자 / 팀원 / 외부 방문자  
> **목표:** 설치 없이 바로 RAG 파이프라인 동작을 확인한다.

---

## 방법 1. 온라인 데모 (설치 불필요, 권장)

### 🌐 연구 사이트
**http://alltology.zapto.org**

- 프로젝트 소개, 연구 배경, 팀 정보 한눈에 확인 가능
- 인터랙티브 실험 결과 포함

---

### 🤗 HuggingFace Spaces — Base RAG vs Conflict-Aware 실시간 비교

**https://huggingface.co/spaces/ponyo03/conflict-aware-rag-demo**

1. 위 링크 접속
2. 질문 입력칸에 아래 중 하나를 입력:
   - `What is knowledge conflict in RAG?`
   - `What color is the Northwood Institute mascot?`
3. **Base RAG** 탭과 **Conflict-Aware** 탭의 답변을 비교
4. 충돌 시나리오에서 두 방법의 차이를 직접 확인

**핵심 관찰 포인트:**
- Base RAG: 문서 충돌을 인식하지 못하고 부정확한 답변 가능
- Conflict-Aware: retrieved 문서를 우선하여 충돌 명시 후 올바른 답변

---

### ✈️ 텔레그램 RAG 봇 — @alltology_rag_bot

저장소 문서(README, docs/)를 지식베이스로 사용하는 RAG 챗봇

1. 텔레그램에서 **@alltology_rag_bot** 검색 또는 아래로 바로 접속
2. `/start` 입력
3. 아래 커맨드로 체험:

| 커맨드 | 설명 |
|--------|------|
| `/about` | 프로젝트 소개 (README 기반) |
| `/run` | 로컬 실행 방법 요약 |
| `/where knowledge conflict` | 저장소에서 키워드 위치 찾기 |
| `/sources` | 최근 답변의 출처 보기 |
| 자유 질문 입력 | 저장소 문서 기반 RAG 답변 |

**예시 질문:**
- `What is the main research question?`
- `How does conflict-aware prompting work?`
- `What datasets are used?`

---

### 🎬 데모 영상

**https://youtu.be/qc0GkgJoBBk**

파이프라인 전체 흐름(Load → Chunk → Embed → Retrieve → Generate)을 영상으로 확인

---

## 방법 2. 로컬 직접 실행 (Python 환경 있는 경우)

> 설치 없이 방법 1로 충분히 확인 가능. 코드 레벨 검증이 필요한 경우만 사용.

### 환경 설정

```bash
git clone https://github.com/Ontology0/Graduation-Project.git
cd Graduation-Project
pip install -r requirements.txt
cp .env.example .env
# .env에 ANTHROPIC_API_KEY 등 입력 (HuggingFace 모델 사용 시 불필요)
```

### Base RAG smoke test

```bash
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

성공 시 콘솔 출력:
```
Experiment: base_rag
Question:   What is knowledge conflict in RAG?
Answer:     ...
Sources:    ...
Saved run:  outputs/runs/<timestamp>.json
```

### Conflict 시나리오 비교

```bash
# Base RAG (충돌 미인식)
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What color is the Northwood Institute mascot?"

# Conflict-Aware (충돌 인식)
python scripts/run_pipeline.py \
  --config configs/experiments/prompting_conflict_aware.yaml \
  --docs data/sample_docs/ \
  --question "What color is the Northwood Institute mascot after the 2019 revision?"
```

실행 결과물: [`outputs/runs/`](outputs/runs/) 참고

---

## 레포 구조

```
src/rag/          ← RAG 파이프라인 (실제 구현)
scripts/          ← CLI 실행 엔트리포인트
configs/          ← 실험 설정(YAML) + 프롬프트(MD)
data/sample_docs/ ← smoke test용 샘플 문서
outputs/runs/     ← 실행 결과 저장 위치
docs/             ← 연구 문서 (architecture, RQ map 등)
```

전체 문서 동선: `README.md` → `docs/architecture.md` → `docs/rq_to_implementation_map.md`

---

## 검증 완료 항목

AI 보조(Claude Code)를 사용해 아래 항목을 검증하였습니다 (2026-05-31).

- [x] 온라인 데모 (HF Spaces, 텔레그램 봇, 연구 사이트) 정상 동작 확인
- [x] 로컬 smoke test 실행 완료 (`outputs/runs/smoke_test_base_rag.json` 생성 확인)
- [x] Conflict 시나리오 비교 실행 완료 (Base vs Conflict-Aware 결과물 커밋)
- [x] `README.md` 충실성: 개요·설치·실행·팀정보·Project Brief 링크 포함
- [x] 필요 파일 존재: `requirements.txt`, `configs/`, `data/sample_docs/`, `src/rag/` 모듈 14개
- [x] 엔트리포인트 실재: `scripts/run_pipeline.py`, `scripts/telegram_bot.py`
- [x] 데모 영상: https://youtu.be/qc0GkgJoBBk
