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

### 1) README 완성도 — 4 / 6점

| 항목 | 내용 |
|------|------|
| **점수** | 4 / 6 |
| **근거(증거)** | README `▶️ 실행` 섹션: `python scripts/run_pipeline.py` 커맨드만 있음. `pip install -r requirements.txt` 설치 단계 없음. 팀 섹션: “팀명: Alltology” 있으나 팀 번호 미기재. `course/elevator_speech_team03.md` 파일명에서 03 유추 가능하나 README 본문에 없음. |
| **감점 사유** | ① 설치 단계(`pip install`) 실행 섹션 첫 화면 부재 (-1점) ② 팀 번호 README 미기재 (-1점) |
| **만점까지 최소 보완** | ① 실행 섹션 상단에 `pip install -r requirements.txt` 추가 ② 팀 섹션에 팀 번호(03) 명시 |

### 2) Human Visitor-Friendly — 3 / 5점

| 항목 | 내용 |
|------|------|
| **점수** | 3 / 5 |
| **근거(증거)** | “처음 보는 사람을 위한 읽는 순서” 섹션 존재 ✅. `docs/architecture.md` Mermaid 포함 ✅. `docs/rq_to_implementation_map.md` RQ↔파일 연결 ✅. `docs/verification_checklist.md` A~D 전 항목 `[ ]` 미체크(commit `1ac0335`에서 추가됐으나 수행 증거 없음). 별도 `LICENSE` 파일 없음(pyproject.toml에 MIT만). |
| **감점 사유** | ① `verification_checklist.md` 체크박스 전부 미완성 — 검증 수행 증거 불가 (-1점) ② 별도 `LICENSE` 파일 부재 (-1점) |
| **만점까지 최소 보완** | ① checklist 실제 수행 후 체크 또는 결과 로그/캡처 첨부 ② 루트에 `LICENSE` 파일 생성(MIT) |

### 3) Project Brief 정합성 — 2 / 5점

| 항목 | 내용 |
|------|------|
| **점수** | 2 / 5 |
| **근거(증거)** | README docs 테이블: `docs/research_plan.md`, `course/`(수업 제출물) 언급됨. 그러나 어떤 문서도 “Project Brief”로 명명·지칭되지 않음. `course/elevator_speech_team03.md`, `course/PMF.md` 등이 brief 역할을 할 수 있으나 README에서 “이게 Project Brief”라는 안내 없음. 평가자가 별도 탐색 없이 즉시 확인 불가. |
| **감점 사유** | ① README에서 “Project Brief = ○○ 파일” 연결 부재 → 정합성 입증 경로 불명확 (-2점) ② `course/` 하위 문서들이 docs 테이블에 연결 미흡 (-1점) |
| **만점까지 최소 보완** | ① README 문서 테이블에 “Project Brief: `course/elevator_speech_team03.md`” 명시 링크 추가 ② `docs/research_plan.md`를 Brief 역할로 명시하거나 별도 `docs/project_brief.md`로 분리 |

### 4) 실제 코드/결과물 존재 — 2 / 5점

| 항목 | 내용 |
|------|------|
| **점수** | 2 / 5 |
| **근거(증거)** | `src/rag/` 10개 모듈 구현됨, `scripts/run_pipeline.py` 실재 ✅. `data/synthetic_conflicts/pilot_conflicts.jsonl` 실재 ✅. 그러나 `outputs/` = `.gitkeep`만(commit `5d1b9b5` 기준), 실제 실행 로그/JSON 전무 ❌. `src/training/train.py` 실행 시 `{“status”: “not_implemented”}` 반환 ❌. `src/evaluation/evaluate.py` = placeholder, 메트릭 없음 ❌. `docs/demo.md` 결과 테이블 전 셀 `TBD`, 데모 URL `TODO` ❌. |
| **감점 사유** | ① `outputs/` 완전 비어있음 — README “outputs/runs/ 아래 결과 생성” 주장과 불일치 (-1점) ② 학습·평가 코드 미구현 scaffold (-1점) ③ 실제 실행 증빙(로그/캡처) 없음 (-1점) |
| **만점까지 최소 보완** | ① smoke test 1회 실행 후 `outputs/runs/` 아래 결과 파일(JSON/MD) 커밋 ② `docs/demo.md` 결과 테이블에 Base RAG 실행 결과 채울 것 |

### 5) 팀 협업 증거 — 3 / 4점

| 항목 | 내용 |
|------|------|
| **점수** | 3 / 4 |
| **근거(증거)** | 커밋 분포: `ryeong03` 63개(54%), `dev-ldy03` 25개(21%), `bbberylll` 18개(15%), `dylee0329` 11개(9%). 3인 실질 기여 확인됨. 커밋 컨벤션 준수. PR 11개, 브랜치 네이밍 전략 실제 사용됨. CONTRIBUTING.md 존재. 그러나 `gh api .../pulls/15/reviews` = 빈 배열 → PR에 reviewer 지정됐으나 **실제 리뷰 승인/코멘트 기록 없음**. |
| **감점 사유** | PR 리뷰 요청만 있고 실제 GitHub review(approve/comment) 기록 없음 — CONTRIBUTING 규칙이 실증되지 않음 (-1점) |
| **만점까지 최소 보완** | 이후 PR에서 reviewer가 GitHub 리뷰 기능으로 실제 comment/approve를 남길 것 |

---

## 별도 평가 — AI 투명성 리포트 (`docs/ai_transparency_report.md`)

**종합 판정: 충분히 구체적이나 구조적 결함과 “예정” 항목 과다가 신뢰도를 낮춤**

| 체크 항목 | 판정 | 근거 |
|-----------|------|------|
| 도구 사용 내역 구체성 | ✅ | 모듈별 AI 생성 내역, 커밋 범위(`4296c12~0de275c`) 명시 |
| 인간 vs AI 역할 분리 | ✅ | 표 형식으로 항목별 명확히 구분 |
| 비판적 판단·검증 흔적 | ⚠️ | “인간 판단” 열에 “승인”이 반복되나 실제 검증 근거는 약함 |
| 커밋과 대조 | ✅ | 언급 커밋 해시 실재 확인됨 |
| 구조적 결함 | ❌ | 섹션 1.6이 섹션 2(인간 주도) 다음에 위치 — append 흔적, 미정리 |
| “예정” 비중 | ❌ | 1.4(데이터), 1.5(실험/평가) 전부 “예정” — 아직 수행되지 않은 단계임을 노출 |

> **감점 신호**: 1.6절 구조 오류는 AI 투명성 리포트가 면밀히 관리된 문서가 아니라 append로 늘어났음을 보여줌. “형식 갖추기” 인상을 줄 수 있음.

---

## 종합

### 내부 정합성 (README↔docs↔configs↔src)

| 쌍 | 판정 | 근거 |
|----|------|------|
| README ↔ src/ 구조 | ✅ | 폴더 설명과 실제 파일 일치 |
| README ↔ docs/ | ✅ | 링크된 파일 모두 실재 |
| architecture.md ↔ scripts/ | ✅ | Key entrypoints 파일 경로 일치 |
| verification_checklist ↔ outputs/ | ❌ | 체크리스트 pass criteria(outputs/runs/ 생성)와 실제 outputs/ 불일치 |
| demo.md 주장 ↔ 실제 산출물 | ❌ | 결과 테이블 TBD, 데모 URL TODO |

### GitHub 레포 합계: 14 / 25점 (데모 영상/스크린샷 항목 제외 기준)

| 항목 | 점수 |
|------|------|
| 1. README 완성도 | 4 / 6 |
| 2. Human Visitor-Friendly | 3 / 5 |
| 3. Project Brief 정합성 | 2 / 5 |
| 4. 실제 코드/결과물 존재 | 2 / 5 |
| 5. 팀 협업 증거 | 3 / 4 |
| **합계** | **14 / 25** |

### 핵심 감점 리스크 Top 3

1. **실제 실행 산출물 부재** (4번 항목 직결) — `outputs/`가 `.gitkeep`만. smoke test 1회 결과라도 커밋이 없으면 루브릭 4번은 절반 이하 점수 고정.
2. **Project Brief 위치 불명확** (3번 항목 직결) — README 어디서도 “Project Brief = 이 파일”이라는 직접 연결 없음. 정합성 입증 불가로 강하게 감점되는 구조.
3. **verification_checklist 미체크 + PR 리뷰 기록 부재** (2번 + 5번 항목 직결) — 체크리스트가 모두 `[ ]`이면 외부 방문자에게 “아무것도 검증 안 했다”는 신호. PR 리뷰 기록 없음도 협업 증거를 문서 규칙 수준으로 격하시킴.

### 엄격 총평

RAG 파이프라인 코드 자체는 모듈 분리·컨벤션·문서화 모두 scaffold 수준 이상으로 성실하게 구성됐고, AI 투명성 리포트 구체성도 평균을 웃돈다. 그러나 “실제로 실행됐다”는 증거가 레포 어디에도 없고, Project Brief 연결 경로가 불명확하며, verification_checklist가 전부 미체크 상태로 제출되었다는 점은 “문서가 주장을 대신한다”는 채점 철학상 결정적 약점이다. 지금 상태는 “좋은 계획서”이지 “검증된 프로젝트”가 아니며, 25점 기준으로 중간값 아래다.
