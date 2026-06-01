# Self-Demo 시연 요령

> **대상:** 이 레포를 처음 보는 평가자 / 외부 방문자  
> **목표:** 설치 없이 5분 안에 프로젝트의 핵심 기능을 직접 체험한다.  
> **준비물:** 인터넷 브라우저, (선택) 텔레그램 앱

---

## 전체 흐름 한눈에 보기

```
1단계  연구 소개 사이트 방문        → 프로젝트 개요 파악
2단계  인터랙티브 데모 체험         → Base RAG vs Conflict-Aware 비교
3단계  텔레그램 RAG 봇 체험        → 저장소 기반 RAG 챗봇 확인
```

---

## 1단계. 연구 소개 사이트

**🌐 http://alltology.zapto.org**

브라우저에서 위 주소를 열면 프로젝트 소개 페이지가 나타납니다.

**확인할 내용:**
- 상단: 연구 주제 및 팀 소개 (팀원 이름, 지도교수, GitHub 링크)
- 스크롤 내리면: 연구 배경 → 핵심 연구 질문 → 연구 접근 방법 순서로 정리됨
- **"앱 데모 보기"** 버튼: HuggingFace Spaces 인터랙티브 데모로 연결
- **"텔레그램 봇 열기"** 버튼: 텔레그램 RAG 봇으로 연결
- **Research** 탭: 진행 중인 실험 내용 및 참고 논문 목록

> 페이지 하단 GitHub 아이콘을 클릭하면 이 저장소로 바로 이동합니다.

---

## 2단계. 인터랙티브 데모 — Base RAG vs Conflict-Aware RAG 비교

**🤗 https://huggingface.co/spaces/ponyo03/conflict-aware-rag-demo**

(또는 연구 사이트에서 "앱 데모 보기" 클릭)

이 데모는 저희 연구의 핵심 질문을 직접 체험하는 공간입니다.  
**"검색된 문서와 AI 내부 지식이 충돌할 때, 어떻게 올바른 답을 낼까?"** 를 두 방법으로 비교합니다.

---

### 실험 A. 샘플 질문으로 기본 동작 확인

1. 페이지 상단 설정이 **"Base RAG"** 인지 확인
2. **"샘플 질문 불러오기"** 버튼 클릭 → 질문이 자동 입력됨
3. **"실행"** 버튼 클릭 → 파이프라인 처리 시간 10~30초 소요
4. 결과 확인:
   - **Answer**: LLM이 생성한 답변
   - **Retrieved Sources**: 답변 근거로 사용된 문서 목록
   - **Final Answer**: 최종 출력

---

### 실험 B. 기업 문서 검색 시나리오 — 실용 적용 사례

> 이 실험은 연구가 실제 현장에서 어떻게 쓰이는지를 보여줍니다.

**상황:** 사내 RAG 시스템에서 직원이 회사 정책을 질문하는 상황입니다.

| | 내용 |
|---|---|
| **AI 내부 학습 지식** | 재택근무는 주 2일까지 허용 (2022년 정책) |
| **사내 문서 시스템(retrieved)** | 2024년 개정: 전면 자율 재택 허용 |

- **Base RAG**: 문서와 모델 내부 지식 중 어느 것을 따를지 불명확하거나 구버전 정책을 답할 수 있음
- **Conflict-Aware RAG**: 정책이 개정되었음을 명시하고 최신 문서를 우선하여 안내

> 법률 문서, 의료 가이드라인, 제품 사양서처럼 **버전이 바뀌는 정보**가 중요한 도메인에서 이 차이가 치명적입니다.

---

### 실험 C. 충돌 시나리오 — 핵심 연구 체험

> 이 실험이 저희 연구의 핵심입니다.

**상황 설명:**  
샘플 문서에는 다음 충돌이 설정되어 있습니다.

| | 내용 |
|---|---|
| **AI 내부 지식 (parametric)** | Northwood Institute 마스코트 색상 = **deep blue** |
| **검색된 외부 문서 (retrieved)** | 2019년 개정 기준 마스코트 색상 = **silver-green** |

**Base RAG로 실험:**
1. 설정: **Base RAG** 유지
2. 질문 입력: `What color is the Northwood Institute mascot?`
3. 실행 → 결과 확인
4. 관찰 포인트: 충돌을 인식하지 못하고 불명확한 답변을 낼 수 있음

**Conflict-Aware RAG로 실험:**
1. 설정을 **"Conflict-Aware Prompting RAG"** 로 변경
2. 동일한 질문 입력: `What color is the Northwood Institute mascot after the 2019 revision?`
3. 실행 → 결과 확인
4. 관찰 포인트:
   - 충돌 존재 여부를 명시적으로 언급하는가?
   - 검색된 문서(silver-green)를 우선하는가?
   - Retrieved Sources 섹션이 동일한 문서를 참조하는가?

---

### 실험 D. 저장소 범위 밖 질문 처리

1. 아무 설정에서나 질문 입력: `삼각형은 각이 몇 개야?`
2. 실행 → 결과 확인
3. 관찰 포인트: 저장소 문서와 무관한 질문에 대해 "문서에 해당 정보 없음" 형태로 응답하는지 확인

> 이는 RAG가 저장소 문서만을 지식 기반으로 사용한다는 것을 보여줍니다.

---

## 3단계. 텔레그램 RAG 봇 — @alltology_rag_bot

(또는 연구 사이트에서 "텔레그램 봇 열기" 클릭)

저장소 문서(README, docs/ 등)를 지식베이스로 사용하는 RAG 챗봇입니다.  
팀원들이 실험 로그·결과를 저장소에 올리면, 봇이 이를 인덱싱해 질문에 답변합니다.

---

### 시작하기

1. 텔레그램 앱에서 **@alltology_rag_bot** 검색
2. `/start` 입력 → "RAG봇이 준비됨" 메시지 확인
3. 아래 커맨드로 체험:

| 커맨드 | 설명 |
|--------|------|
| `/about` | 프로젝트 소개 (README 기반 RAG 답변) |
| `/run` | 로컬 실행 방법 요약 |
| `/where knowledge conflict` | 저장소 내 키워드 위치 찾기 |
| `/status` | 현재 인덱스 상태 확인 |
| `/sources` | 최근 답변의 출처 문서 확인 |
| 자유 질문 | 저장소 문서 기반 RAG 답변 |

**추천 질문:**
- `What is the main research question?`
- `How does conflict-aware prompting work?`
- `What is knowledge conflict in RAG?`

---

### 접근 권한 등록 (보안 정책)

> 봇은 허가된 사용자만 이용 가능합니다. 접근이 제한된 경우 아래 절차를 따르세요.

1. `/whoami` 입력 → 본인의 Telegram User ID 확인
2. 해당 ID를 팀에 공유하면 허용 목록에 등록해드립니다

**보안 정책을 적용한 이유:**  
이 봇은 Telegram API, LLM API, Railway 백엔드 서버와 연결되어 있어 외부 비용이 발생하고, 무단 사용 시 보안 이슈가 생길 수 있습니다. 따라서 팀원 및 허가된 사용자만 이용 가능하도록 User ID 기반 allowlist를 운영합니다.

---

## 데모 영상

전체 시연 흐름을 영상으로 확인할 수 있습니다.

**🎬 https://youtu.be/qc0GkgJoBBk**

---

## 로컬 직접 실행 (선택 사항)

> 위 온라인 데모로 충분히 확인 가능합니다. 코드 레벨 검증이 필요한 경우만 아래를 따르세요.

```bash
git clone https://github.com/Ontology0/Graduation-Project.git
cd Graduation-Project
pip install -r requirements.txt
cp .env.example .env   # 필요 시 API 키 입력 (HF 모델 사용 시 불필요)

# Base RAG smoke test
python scripts/run_pipeline.py \
  --config configs/experiments/rag_base.yaml \
  --docs data/sample_docs/ \
  --question "What is knowledge conflict in RAG?"
```

성공 시 콘솔에 `Experiment / Question / Answer / Sources` 출력 후  
`outputs/runs/` 아래 `.json` / `.md` 결과 파일 자동 생성.

실제 실행 결과물 예시: [`outputs/runs/smoke_test_base_rag.json`](outputs/runs/smoke_test_base_rag.json)

---

## 검증 완료 항목

AI 보조(Claude Code)를 사용해 아래 항목을 검증하였습니다 (2026-05-31).

- [x] 온라인 데모 (HF Spaces, 텔레그램 봇, 연구 사이트) 정상 동작 확인
- [x] 텔레그램 봇 live 테스트: 질문 응답, HTML 포맷 렌더링, Railway 연결 확인
- [x] 로컬 smoke test 실행 완료 (`outputs/runs/smoke_test_base_rag.json` 생성 확인)
- [x] Conflict 시나리오 비교 실행 완료 (Base vs Conflict-Aware 결과물 커밋됨)
- [x] `README.md` 충실성: 개요·설치·실행·팀정보·Project Brief 링크 포함
- [x] 필요 파일 존재: `requirements.txt`, `configs/`, `data/sample_docs/`, `src/rag/` 모듈 14개
- [x] 엔트리포인트 실재: `scripts/run_pipeline.py`, `scripts/telegram_bot.py`
- [x] 데모 영상: https://youtu.be/qc0GkgJoBBk
