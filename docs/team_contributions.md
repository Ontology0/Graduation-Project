# 팀원별 활동과 근거

> 업데이트: 2026-10-27. 회의록의 작성·담당 기록과 GitHub 등록 이력을 연결합니다. 커밋 수나 업로더만으로 연구 기여율·단독 저작을 판단하지 않습니다.

## 현재 학기 활동 근거

| 팀원 | 기록으로 확인할 수 있는 활동 | 근거 |
|---|---|---|
| **박세령** (@ryeong03) | 팀 회의록 작성, 면담 결과 보고, 발표 코드 공유·저장소 안내 정리 | [10/15 작성 회의록](meeting-log/2026-10-15_회의록.md), [9/15 면담 후 보고 기록](meeting-log/2026-09-15_회의록.md), [9/10 등록 커밋](https://github.com/Ontology0/Graduation-Project/commit/700737c), [발표 코드·출처 안내](../experiments/presentation/README.md) |
| **손현경** (@bbberylll) | Steering 개발본, P6/P9·E0/E1/E15/E17 등 실험 코드와 10/22 회의록 등록 | [9/22 Steering 등록](https://github.com/Ontology0/Graduation-Project/commit/f90e3d1), [10/22 실험 묶음 등록](https://github.com/Ontology0/Graduation-Project/commit/0660cb6), [10/22 회의록 등록](https://github.com/Ontology0/Graduation-Project/commit/1f06c1a) |
| **이다영** (@dev-ldy03) | 면담 회의록 작성, E2·A3 및 A0/A1 코드·결과, 비교 하네스 등록 | [10/13 작성 회의록](meeting-log/2026-10-13_회의록.md), [E2 분석 등록](https://github.com/Ontology0/Graduation-Project/commit/c137228), [A3 등록](https://github.com/Ontology0/Graduation-Project/commit/c7a1b0f), [A0/A1 결과·SOTA 정리](https://github.com/Ontology0/Graduation-Project/commit/5988255) |

회의록 작성자와 GitHub 업로더가 다른 경우 두 역할을 구분합니다. 공동 연구의 설계·실행·해석 기여 전체를 이 표의 등록 내역만으로 환산하지 않습니다. 논문용 자료를 공개하지 않아도 기존 회의·발표·개발 기록으로 활동 경과를 확인할 수 있습니다.

## 팀 보고에서 확인할 연구 내용

| 자료 | 주요 분석 | 코드·결과 연결 |
|---|---|---|
| [다영 외부 Always·Router 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.ip6i2nm6wvrb) | 일괄 개입의 C+ 손상, 입력별 이득 예측의 효과, 강도 조절만으로 해결되지 않는 한계 | [A0/A1](../experiments/README.md#먼저-볼-코드), [ConFiQA Router 실행본](https://drive.google.com/file/d/1ghpS2MP4XSeBh8R8t_Ay7KSN-o4PZcAG/view) |
| [현경 Packed 외부 분석](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.6grhiq4uqc72) | 두 분기 선택·온라인 방향 추정, X1이 잘못된 기억을 고르는 실패, 조건별 audit와 후속 검증 | [E17 개발·진단](../experiments/E17/), [보고 수치·조건](research_status.md) |
| [발표·선행 내부 신호 실험](../experiments/presentation/README.md) | head·레이어 신호, 규칙과 판독기, 온라인 개입 경로의 구분 | [공유 원본 출처](../experiments/drive_sources.json); 가져오기와 연구 수행을 구분 |

현재 소개는 어느 한 사람의 상태 판독 자료만이 아니라 위 보고와 팀 회의의 Routing 방향을 함께 반영합니다. 자료별 독립 조건을 합쳐 하나의 완성된 결합 모델이라고 표현하지 않습니다.

## 공동 작업과 후속 과제

- [10/13 면담](meeting-log/2026-10-13_회의록.md) → [10/15 팀 회의](meeting-log/2026-10-15_회의록.md): Routing 중심 방향, 행동·강도·내부 신호·비용 비교 과제를 구체화했습니다.
- [10/22 팀 회의](meeting-log/2026-10-22_회의록.md): Steering 관련 논문을 팀원별 2편씩 리뷰하기로 계획했습니다. 이 계획만으로 리뷰 완료를 표시하지 않습니다.
- 기존 Router, 온라인 Router, Packed의 구현·조건을 구분하고 교차 확인하는 과제는 [연구 계획](research_plan.md)에 연결합니다.
- 10/27 문서 정리·링크 검증에는 AI 보조를 사용했으며, 새 모델 실험을 수행한 것으로 표시하지 않습니다. [AI 활용 기록](ai_transparency_report.md)

## Start 단계 기여 기록

아래는 초기 RAG·DPO/LoRA 단계의 기존 기록입니다. 현재 학기 Routing·Packed의 담당표와 구분합니다.

| 팀원 | 주요 담당 | GitHub evidence |
|------|-----------|-------------------|
| **박세령** (@ryeong03) | conflict 문제 정의, RAG pipeline 설계·구현, verification·CI, 데모/smoke 문서 | [PR #81](https://github.com/Ontology0/Graduation-Project/pull/81) (GitHub Actions + evaluate Arm 1·2), [PR #76](https://github.com/Ontology0/Graduation-Project/pull/76) (CI scaffold), [PR #71](https://github.com/Ontology0/Graduation-Project/pull/71) (README 실행 결과물), [issue #59](https://github.com/Ontology0/Graduation-Project/issues/59) (verification checklist) |
| **이다영** (@dev-ldy03) | 데이터 파이프라인, 평가 설계, 파일럿 실험 결과 정리 | [PR #80](https://github.com/Ontology0/Graduation-Project/pull/80) (exp1 설계·채점 구분), [PR #68](https://github.com/Ontology0/Graduation-Project/pull/68) / [issue #56](https://github.com/Ontology0/Graduation-Project/issues/56) (5-arm 평가 하네스), [issue #55](https://github.com/Ontology0/Graduation-Project/issues/55) (benchmark train/eval split) |
| **손현경** (@bbberylll) | DPO 학습 방향 설계, LoRA fine-tuning scaffold, 발표·문서 | [PR #69](https://github.com/Ontology0/Graduation-Project/pull/69) (DPO training), [issue #54](https://github.com/Ontology0/Graduation-Project/issues/54) (DPO 파이프라인), [PR #74](https://github.com/Ontology0/Graduation-Project/pull/74) (main 반영) |

## 협업 방식 (요약)

- **브랜치:** `dev` 통합 → milestone 시 `main` (see `CONTRIBUTING.md`)
- **이슈·PR:** `feat/`, `docs/`, `fix/` 태그 + 이슈 번호 참조
- **Co-authored-by:** AI 보조 커밋에 `Co-authored-by: Cursor` 등 명시 (투명성)

## 관련 문서

- [교수님 검토 안내](review_guide.md) — 전체 활동과 개발·검증 근거
- [`docs/rq_to_implementation_map.md`](rq_to_implementation_map.md) — 초기 RAG 단계 RQ ↔ 코드 정합성
- [`docs/verification_checklist.md`](verification_checklist.md) — 초기 구현의 재현·운영 검증 기록
- [`docs/ai_transparency_report.md`](ai_transparency_report.md) — AI 활용 투명성
