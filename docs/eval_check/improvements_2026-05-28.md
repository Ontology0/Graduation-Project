## 2026-05-28 기준 개선점 (capstone-final-eval 루브릭 기반)

본 문서는 이화여대 캡스톤디자인 기말 평가 루브릭(`docs/eval_check/capstone-final-eval-SKILL.md`) 관점에서, 현재 GitHub 레포/문서/데모 구성의 **부족한 점과 개선 방향**을 기록한다.  
전제: 본 저장소는 연구 스캐폴드이며 최종 실험 결과는 아직 없음(README에 명시).

---

### 1) GitHub 레포 평가 — Human Visitor-Friendly

#### (1) 데모 증빙의 “한 눈에 보임” 부족

- **증상**: 외부 방문자가 “무엇이 실제로 동작하는지(데모)”를 README 첫 화면에서 바로 찾기 어렵다.
- **리스크(감점 포인트)**: “라이브 데모/실제 코드 존재” 항목에서 인상이 약해짐.
- **개선안**
  - `README.md` 상단에 “Demo/Quickstart” 링크 블록 추가
  - `docs/demo.md`에 텔레그램 봇/CLI 시연 스크린샷(또는 짧은 GIF/영상 링크) 1개 이상 추가

#### (2) 아키텍처를 요약하는 시각 자료 부족

- **증상**: RAG 흐름과 봇 레이어의 관계가 텍스트로는 설명되나, 평가자가 한 장으로 이해하기 어렵다.
- **개선안**
  - `docs/architecture.md` 신설: Load→Chunk→Embed→Index→Retrieve→Prompt→Generate + Telegram layer를 1페이지로 정리
  - README에서 `docs/architecture.md`를 바로 링크

#### (3) “운영 문서 존재”는 좋으나 탐색성이 더 좋아질 여지

- **현황**: 운영/비용/보안은 `docs/telegram_bot_ops.md`로 분리되어 있음(장점).
- **개선안**
  - README의 봇 섹션에 운영 문서 링크를 더 명시적으로(“운영/비용/보안: …”) 표기

---

### 2) GitHub 레포 평가 — Project Brief/보고서와의 정합성

#### (1) 연구 목표(Conflict-aware PA-RAG) ↔ 구현물(RAG 파이프라인/봇)의 “매핑 문서” 부족

- **증상**: 구현이 존재해도 “이 구현이 어떤 연구 질문을 어떻게 검증하려는지”가 한 문서로 연결되어 있지 않다.
- **개선안**
  - `docs/rq_to_implementation_map.md` 신설
    - RQ/가설 → 관련 문서(`docs/*`) → 실험 설정(`configs/experiments/*`) → 코드 엔트리포인트(`src/*`, `scripts/*`)로 링크 매핑

#### (2) Implemented vs Planned vs TBD 경계는 있으나 더 구조화 가능

- **증상**: README에 스캐폴드 상태가 적혀 있지만, 평가자가 빠르게 훑기엔 구조가 더 단단해질 수 있다.
- **개선안**
  - README에 체크리스트/표 형태로 “Implemented / Planned / TBD” 섹션 정리(과장 금지)

---

### 3) “실제 코드/결과물 존재”를 더 강하게 만드는 포인트

#### (1) 원클릭(원커맨드) 재현성 부족

- **증상**: 여러 단계가 흩어져 있어 평가자가 “한 번에 실행”하기 어렵다.
- **개선안**
  - `scripts/quickstart_demo.sh` 또는 `Makefile`(`make demo`) 추가
    - 예: 인덱스 로드/빌드 → 샘플 질문 → outputs 생성 확인까지 한 번에

#### (2) outputs 산출물은 “예시 경로/형태”를 문서로만 증명해도 충분

- **증상**: 실험 결과가 아직 없으므로 outputs 자체를 레포에 넣기 어렵다.
- **개선안**
  - `docs/demo.md`에 “실행 후 생성되는 파일” 예시 경로(`outputs/runs/*.json`, `*.md`)와 캡처 이미지 추가

---

### 4) AI 투명성 리포트(발표/보고서 공통) 관점 개선 포인트

#### (1) “AI 사용”보다 “인간의 판단/검증”이 더 전면에 보이게 구조화

- **현황**: `docs/ai_transparency_report.md`에 작업 내역이 기록되어 있음.
- **개선안**
  - 보고서/발표에서 아래를 명시적으로 강조
    - 선택한 대안과 배제한 대안(예: 서버리스 운영 시 수동 `/reindex`, 민감 커맨드 기본 잠금)
    - 검증 체크리스트(실행 로그/재현 단계)와 실패 케이스 처리

#### (2) “재현 가능한 검증 절차”를 docs에 고정

- **개선안**
  - `docs/demo.md` 또는 별도 `docs/verification_checklist.md`에
    - allowlist 미설정 시 민감 커맨드 차단 확인
    - 인덱스 재사용(`retrieval.index_dir`) 확인
    - Telegram 포맷(HTML) 렌더링 확인
    를 체크리스트로 추가

---

### 5) 우선순위(추천)

1. **README 상단 Demo/Quickstart 링크 강화 + demo 증빙(스크린샷/영상)**  
2. **`docs/architecture.md` 1페이지 아키텍처 요약 추가**  
3. **RQ↔구현 매핑 문서(`docs/rq_to_implementation_map.md`) 추가**  
4. 원커맨드 실행 스크립트(`make demo` 또는 `scripts/quickstart_demo.sh`)  
5. 검증 체크리스트 문서화(투명성/재현성 강화)

