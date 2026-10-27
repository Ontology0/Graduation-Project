# 문서 안내

> 업데이트: 2026-10-27. 최신 연구 방향과 이전 기록을 구분해 안내합니다.

## 현재 연구

| 문서 | 내용 |
|---|---|
| [교수님 검토 안내](review_guide.md) | 10/13 공지 대응, 활동→결정→개발 산출물, 검증 사례·후속 일정 |
| [저장소 소개](../README.md) | 문제·두 연구 축·주요 결과·코드 안내 |
| [팀원별 활동 근거](team_contributions.md) | 현재 학기 협업·등록 근거와 Start 단계 기여 구분 |
| [AI 활용 기록](ai_transparency_report.md) | 10/27 저장소 정리 범위와 초기 개발 보조 기록 구분 |
| [Project Brief](project_brief.md) | 현재 연구의 목표와 산출물 요약 |
| [연구 결과와 근거](research_status.md) | 발표·10/27 보고·공개 산출물의 수치와 조건 |
| [연구 계획](research_plan.md) | 관찰→방법 흐름, 다음 과제·평가 계획 |
| [실험 안내](../experiments/README.md) | 노트북 목적·입력·공개 결과 |
| [기말발표용 코드](../experiments/presentation/README.md) | 공유 Drive의 발표·선행 실험 8개와 현재 Routing·Packed 연결 |
| [SOTA 안내](../SOTA/README.md) | 비교 코드의 구현 상태와 실행 전제 |
| [공용 규격](../prompt/p8s_prompt.py) | P8S 프롬프트·채점·생성 설정 |

## 회의와 원문 자료

[교수님 미팅 자료 원문](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit)은 7월 탐색부터 10월 27일 보고까지 여러 탭으로 구성돼 있습니다. 최신 결과는 14회차 보고를 기준으로 읽고, 과거 설계·철회된 설정과 구분하세요. 제공된 발표·미팅 PDF의 사용 범위는 [근거 목록](research_status.md#출처와-읽는-순서)에 정리했습니다.

| 날짜 | 기록 |
|---|---|
| [10/27 서면 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.xhbic2nnwq8w) | 외부 Router·Packed 평가, X1 손상과 후속 과제; 교수님 결정 회의록과 구분 |
| [10/22 팀 회의](meeting-log/2026-10-22_회의록.md) | 10/15 후속 연구·논문 리뷰·저장소 정리 |
| [10/20 팀 회의](meeting-log/2026-10-20_회의록.md) | 한이음 최종본 일정·개발 산출물 점검 |
| [10/15 팀 회의](meeting-log/2026-10-15_회의록.md) | Routing 후속 과제·4-state 논문 심사용 제출 |
| [10/13 면담](meeting-log/2026-10-13_회의록.md) | Routing 중심 전환·One-pass·외부 평가 |
| [9/29 면담](meeting-log/2026-09-29_회의록.md) | head 판독과 steering 방향 분리·라벨 범위 |
| [9/22 면담](meeting-log/2026-09-22_회의록.md) | hidden 표현·개입 이득 기반 routing |
| [9/15 면담](meeting-log/2026-09-15_회의록.md) | 내부 신호·실험 논의 |
| [9/10 팀 회의](meeting-log/2026-09-10_회의록.md) · [9/8 면담](meeting-log/2026-09-08_회의록.md) · [9/3](meeting-log/2026-09-03) | 이전 논의 |

전체 원문은 [meeting-log/](meeting-log/)에 보존합니다. 당시 제안과 후속 과제를 완료 결과로 바꾸어 읽지 않습니다.

## 초기 PA-RAG·수업·데모 기록

아래는 주로 2026년 1학기 기록입니다. 현재 Routing·Packed의 방법·실행 상태를 설명하는 문서가 아니며, 당시 경로·외부 데모 운영 상태는 현재와 다를 수 있습니다.

| 자료 | 당시 내용 |
|---|---|
| [Start 소개](archive/start-overview.md) · [Start Project Brief](archive/start-project-brief.md) | 초기 README·DPO/LoRA 구상·파일럿·데모 |
| [실험 설계](experiment_design.md) · [RQ–구현 매핑](rq_to_implementation_map.md) | PA-RAG 5-arm 비교 계획 |
| [Architecture](architecture.md) · [Demo](demo.md) · [검증 기록](verification_checklist.md) | 초기 RAG 파이프라인 |
| [관련 연구](related_work.md) · [벤치마크 검토](benchmark_selection.md) · [Decision log](decision_log.md) | 초기 선행 연구·데이터 검토 |
| [수업 AI 활용 기록](../course/transparency_report.md) | 초기 단계 활용·계획; 현재 연구 전체의 완료 내역이 아님 |
| [발표 원고](presentation.md) · [발표 PDF](presentation/presentation.pdf) | 초기 발표; 이번에 제공된 58쪽 발표와 구분 |
| [텔레그램 운영](telegram_bot_ops.md) · [Self-demo](../self_demo.md) | 초기 데모 안내 |
| [이전 실험](../legacy/experiments/) · [이전 실행 결과](../legacy/outputs/) | 파일럿·이전 산출물 |

한이음 설계는 [hanium-design-v0.3.md](han_eum_docs/hanium-design-v0.3.md)에 별도 보관합니다.
