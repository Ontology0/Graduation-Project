# 문서 길잡이

> 문서 업데이트: 2026-10-29. 연구 소개, 활동 기록, 코드·결과를 목적에 맞게 찾아볼 수 있습니다.

## 목적에 맞게 시작하기

| 목적 | 첫 문서 | 이어서 볼 자료 |
|---|---|---|
| 프로젝트가 낯설다 | [처음 읽는 안내](getting_started.md) | [짧은 소개·강점](project_brief.md), [첫 결과 CSV](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_policies.csv) |
| 연구 진행과 팀 활동을 살펴본다 | [연구 활동과 주요 산출물](review_guide.md) | 아래 회의록, [팀원별 활동](team_contributions.md) |
| 실험을 이해하거나 참여한다 | [실험별 코드 지도](../experiments/README.md) | [평가 조건·결과](research_status.md), [다음 연구](research_plan.md), [기여 규칙](../CONTRIBUTING.md) |
| 예전 자료가 필요하다 | [이전 연구 보관함](archive/README.md) | 초기 RAG·DPO/LoRA, 데모, 이전 발표·자체점검 |

현재 설명의 중심은 **내부 신호를 이용한 선택적 개입과 답변 개선**입니다. 별도 4-state 논문은 심사 중이며, 논문용 코드·상세 결과는 공개 보류합니다.

## 현재 연구 자료

| 자료 | 내용 |
|---|---|
| [제출용 Project Brief](project_brief.md) | 트랙·한 줄 주제·키워드·강점 및 특징 8문장 |
| [연구 결과와 근거](research_status.md) | 공개 결과·외부 보고의 표본, 라벨 사용, 수치·한계 |
| [연구 계획](research_plan.md) | 관찰→설계, 다음 질문·평가 원칙·미완료 과제 |
| [실험 안내](../experiments/README.md) | 질문별 시작 코드와 전체 노트북·입력 목록 |
| [발표·선행 코드](../experiments/presentation/README.md) | 내부 신호·온라인 개입의 선행 실험; 최신 연구 전체와 구분 |
| [SOTA 안내](../SOTA/README.md) | 비교 하네스의 구현·미구현·실행 전제 |
| [공용 프롬프트·채점](../prompt/p8s_prompt.py) | P8S 실행 규격 |
| [팀 활동 근거](team_contributions.md) · [AI 활용 기록](ai_transparency_report.md) | 협업·보고·등록과 문서 정리 범위 |

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

## 이전 연구와 별도 프로젝트

초기 문서는 [이전 연구 보관함](archive/README.md), 당시 코드·설정·수업 자료는 [legacy/](../legacy/README.md)에서 찾을 수 있습니다. 초기 웹·봇 데모와 자체평가 자료를 현재 연구의 실행법이나 공식 채점 결과로 사용하지 않습니다.

한이음 설계는 [hanium-design-v0.3.md](han_eum_docs/hanium-design-v0.3.md)에 별도 보관합니다.
