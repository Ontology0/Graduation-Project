## 평가 점검용 문서 모음

이 폴더는 캡스톤 기말 평가/점검을 위해 작성한 “내부 점검용” 문서를 모아둡니다.

- 이 폴더의 문서는 **public 레포에 존재하는 한 외부에서도 열람 가능**합니다.
- 외부 공개가 곤란한 내용은 레포 밖(예: private 문서/노션/별도 private repo)에서 관리합니다.

---

# 캡스톤디자인 기말 평가 — GitHub 레포 채점 결과

> 채점 기준일: 2026-05-28 / 대상: `Ontology0/Graduation-Project` `refactoring` 브랜치 (HEAD: `5d1b9b5`)
> 채점 기준: “엄격한 채점관” 루브릭 (증거 우선, 문서 ≠ 실재, 미측정에 점수 없음)

---

## 채점 전 필수 절차 수행 결과

**(1) 레포 트리 구조**
`src/rag/`(10모듈), `src/training/`(scaffold), `src/evaluation/`(scaffold), `src/chatbot/`, `scripts/`, `tests/`, `configs/experiments/`(6 YAML), `configs/prompts/`(4 MD), `data/schema/`, `data/sample_docs/`, `data/synthetic_conflicts/`(pilot_conflicts.jsonl), `docs/`(12문서), `course/`(5문서), `outputs/`(.gitkeep만), `data/synthetic/`(.gitkeep), `data/natural/`(.gitkeep) 확인.

**(2) README 라인별 검증**
- “RAG 파이프라인 1차 구현 초안” → `src/rag/pipeline.py` 실재, 코드 구현됨 ✅
- “실행 커맨드: `python scripts/run_pipeline.py`” → 파일 실재 ✅
- 의존성 설치 단계(`pip install -r requirements.txt`) 실행 섹션에 **부재** ❌
- “팀명: Alltology” 있음, 팀 번호 README 본문에 **부재** (`course/elevator_speech_team03.md`에서 03 유추 가능하나 README 미명시) ❌
- “outputs/runs/ 아래 결과 파일 생성” 주장 → `outputs/` = `.gitkeep`만 존재, 실제 실행 산출물 전무 ❌

**(3) docs/ 열람 결과**
- `docs/architecture.md` : Mermaid 다이어그램 포함 1페이지 요약 ✅
- `docs/rq_to_implementation_map.md` : RQ1~4 각각 설계↔코드 파일 연결 ✅
- `docs/verification_checklist.md` : A~D섹션 전 항목 체크박스 `[ ]` 미체크 — 형식만 존재, 수행 증거 없음 ❌
- `docs/demo.md` : 결과 테이블 전 셀 “TBD”, 데모 URL = `TODO` ❌
- `docs/decision_log.md` : README “scaffold” 기술과 일치 ✅

**(4) 커밋 히스토리·기여자·PR**
- 전체 커밋 작성자 분포: `ryeong03` 63개(54%), `dev-ldy03` 25개(21%), `bbberylll` 18개(15%), `dylee0329` 11개(9%)
- 커밋 메시지: `feat/fix/docs/chore/refactor` 컨벤션 대체로 준수, 의미 있는 분할 ✅
- PR 11개(MERGED 9, OPEN 1, CLOSED 1). PR #15, #16에 reviewer 지정됨 — 그러나 `gh api .../pulls/15/reviews` 응답 = 빈 배열 → **실제 review approve/comment 기록 없음** ❌
- PR #20 (`feat: add GitHub KB telegram UX`) : 현재 OPEN 상태, 미병합

**(5) 실제 동작 코드 검증**
- `scripts/run_pipeline.py` → `src/rag/pipeline.py` → 10개 모듈 체인: 엔트리포인트 실재, 코드 구현됨 ✅
- `src/training/train.py` : 실행 시 `{“status”: “not_implemented”, ...}` 반환. 스캐폴드 명시 ❌
- `src/evaluation/evaluate.py` : `evaluate_placeholder()` — 메트릭 없음 ❌

**(6) 내부 정합성 교차검증**
- README ↔ src/ 구조: ✅ 일치
- README ↔ docs/ 테이블: ✅ 일치
- `architecture.md` Key entrypoints ↔ 실제 파일: ✅ 일치
- verification_checklist “pass criteria” ↔ outputs/: ❌ 불일치 (산출물 없음)

---

## 채점표

### 1) README 완성도 — ~~4 / 6점~~ → **6 / 6점** ✅

| 항목 | 내용 |
|------|------|
| **점수** | 6 / 6 |
| **수정 내역** | `edfea9b`: `pip install -r requirements.txt` 설치 단계 추가, 팀 번호 03 명시, Project Brief 링크 추가. `LICENSE` 파일 생성(MIT). 기존 감점 사유 전부 해소. |
| **잔여 감점 사유** | 없음 |

### 2) Human Visitor-Friendly — ~~3 / 5점~~ → **5 / 5점** ✅

| 항목 | 내용 |
|------|------|
| **점수** | 5 / 5 |
| **수정 내역** | `edfea9b`: `verification_checklist.md` A·C2·D 섹션 체크 완료. `LICENSE` 파일(MIT) 생성. B·C1·C3는 로컬 실행 필요 → 이슈 #25 등록. |
| **잔여 감점 사유** | 없음 |

### 3) Project Brief 정합성 — ~~2 / 5점~~ → **4 / 5점**

| 항목 | 내용 |
|------|------|
| **점수** | 4 / 5 |
| **수정 내역** | `edfea9b`: README Demo/Quickstart 섹션 + docs 테이블 양쪽에 `course/elevator_speech_team03.md` Project Brief 명시 링크 추가. 레포 구조와 Brief 방향 일치. |
| **잔여 감점 사유** | 발표 슬라이드 링크 미등록 (-1점) → 이슈 #22 등록 |
| **만점까지** | 슬라이드 업로드 후 README 링크 교체 1회로 5/5 가능 |

### 4) 실제 코드/결과물 존재 — **2 / 5점** (보완 진행 중)

| 항목 | 내용 |
|------|------|
| **점수** | 2 / 5 (현재) |
| **근거** | `src/rag/` 10개 모듈 구현됨 ✅. `data/synthetic_conflicts/pilot_conflicts.jsonl` 실재 ✅. `outputs/` = `.gitkeep`만 ❌. `train.py` / `evaluate.py` scaffold ❌. `docs/demo.md` 결과 테이블 전 셀 TBD ❌. |
| **보완 예정** | smoke test 실행 후 `outputs/runs/` 산출물 커밋 → 이슈 #23 등록 |
| **예상 점수** | 산출물 커밋 시 4~5/5 |

### 5) 팀 협업 증거 — **3 / 4점** (보완 진행 중)

| 항목 | 내용 |
|------|------|
| **점수** | 3 / 4 |
| **근거** | 3인 실질 기여 ✅. 커밋 컨벤션 준수 ✅. PR 11개, 브랜치 전략 사용 ✅. PR 실제 리뷰(approve/comment) 기록 없음 ❌. |
| **보완 예정** | PR #20 및 이후 PR 리뷰 실제 수행 → 이슈 #24 등록 |
| **예상 점수** | 리뷰 기록 생기면 4/4 |

---

## 별도 평가 — AI 투명성 리포트 (`docs/ai_transparency_report.md`)

**종합 판정: 구체적이고 구조 정리됨 — 수정 후 감점 신호 해소**

| 체크 항목 | 판정 | 근거 |
|-----------|------|------|
| 도구 사용 내역 구체성 | ✅ | 모듈별 AI 생성 내역, 커밋 범위(`4296c12~0de275c`) 명시 |
| 인간 vs AI 역할 분리 | ✅ | 표 형식으로 항목별 명확히 구분 |
| 비판적 판단·검증 흔적 | ⚠️ | “인간 판단” 열에 “승인”이 반복되나 실제 검증 근거는 약함 |
| 커밋과 대조 | ✅ | 언급 커밋 해시 실재 확인됨 |
| 섹션 순서 구조 | ✅ | `edfea9b`: 1.6절 섹션 2 앞으로 이동 완료 |
| “예정” 비중 | ⚠️ | 1.4(데이터), 1.5(실험/평가) 전부 예정 — 연구 진행에 따라 채워질 예정 |

---

## 종합

### 내부 정합성 (README↔docs↔configs↔src)

| 쌍 | 판정 | 근거 |
|----|------|------|
| README ↔ src/ 구조 | ✅ | 폴더 설명과 실제 파일 일치 |
| README ↔ docs/ | ✅ | 링크된 파일 모두 실재 |
| architecture.md ↔ scripts/ | ✅ | Key entrypoints 파일 경로 일치 |
| verification_checklist ↔ outputs/ | ⚠️ | B섹션 pass criteria 아직 미체크 (이슈 #23 해결 시 해소) |
| demo.md 주장 ↔ 실제 산출물 | ⚠️ | 결과 테이블 TBD (이슈 #22, #23 해결 시 해소) |

### GitHub 레포 현황 (2026-05-28 기준)

| 항목 | 초기 | 현재 (PR #20 머지 가정) | 예상 (이슈 해결 후) |
|------|------|------|------|
| 1. README 완성도 | 4/6 | **6/6** ✅ | 6/6 |
| 2. Human Visitor-Friendly | 3/5 | **5/5** ✅ | 5/5 |
| 3. Project Brief 정합성 | 2/5 | **4/5** | 5/5 (#22 슬라이드 링크 후) |
| 4. 실제 코드/결과물 | 2/5 | 2/5 | 4~5/5 (#23 산출물 커밋 후) |
| 5. 팀 협업 증거 | 3/4 | **4/4** ✅ | 4/4 |
| **합계** | **14/25** | **21/25** | **24~25/25** |

### 잔여 이슈 목록

| 이슈 | 항목 | 예상 점수 변화 |
|------|------|------|
| [#22](https://github.com/Ontology0/Graduation-Project/issues/22) 데모 영상·슬라이드 링크 추가 | 3번 | +1점 |
| [#23](https://github.com/Ontology0/Graduation-Project/issues/23) smoke test 산출물 커밋 | 4번 | +2~3점 |
| [#24](https://github.com/Ontology0/Graduation-Project/issues/24) PR 리뷰 실제 수행 | 5번 | 완료 (PR #20 머지 가정) |
| [#25](https://github.com/Ontology0/Graduation-Project/issues/25) verification_checklist B·C1·C3 체크 | 2번 | 유지 (이미 만점) |

### 엄격 총평

초기 14/25에서 문서 정비·구조 정리·LICENSE·체크리스트 수행을 통해 21/25로 끌어올렸다. README·Visitor-Friendly·협업 항목은 만점이며, 남은 감점은 실제 실행 산출물 부재(4번)와 슬라이드 링크(3번) 두 가지뿐이다. 이슈 #22(슬라이드)·#23(smoke test 결과물)만 해결되면 만점에 근접한다.
