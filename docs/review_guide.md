# 교수님 검토 안내 — 활동과 개발 산출물

> 기준: `CapstoneDesign-Announcement (10.13).pdf` 및 `CapstoneDesign-After progress presentation.pdf` · 정리일: 2026-10-27
>
> **회의에서 무엇을 논의했고, 무엇을 구현·검증했으며, 무엇이 남았는지**를 원본 기록과 코드로 연결합니다. 논문 심사용 코드·결과는 공개 보류 상태입니다.

## 1. 먼저 확인할 자료

| 확인 순서 | 자료 | 확인할 내용 |
|---|---|---|
| ① 연구 개요 | [제출용 Project Brief](project_brief.md) · [처음 읽는 안내](getting_started.md) | 왜 필요한가 → 선택적 개입 → 근거와 한계 |
| ② 활동 경과 | 아래 활동 흐름 · [날짜별 회의록 목록](README.md#회의와-원문-자료) | 피드백과 연구 방향 변경, 후속 과제 |
| ③ 실제 개발 | [실험 안내](../experiments/README.md) · [발표 코드 8개](../experiments/presentation/README.md) | 구현한 실험, 입력·환경, 원본 출처 |
| ④ 검증 근거 | [A1 정책 CSV](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_policies.csv) · [연구 결과와 근거](research_status.md) | 저장 결과, 외부 보고값, 성과와 한계 |
| ⑤ 협업과 다음 단계 | [팀원별 활동 근거](team_contributions.md) · [연구 계획](research_plan.md) | 담당 기록, 기여 증빙, 미완료 작업 |

GPU 실행 없이 회의록·코드·CSV를 열어 진행 내용을 확인할 수 있습니다. 전체 실험 재실행에는 모델 접근 권한·선행 입력·GPU 등이 필요하며, 준비 조건은 [실험 안내](../experiments/README.md#실행에-필요한-입력)를 따릅니다.

### 중간발표 공통 피드백 반영

`CapstoneDesign-After progress presentation.pdf` 2쪽은 **10/27까지 트랙·한 줄 주제·키워드·강점 및 특징 취합**을 안내하며, 최종발표 심사위원에게 제공할 자료라고 설명합니다. 9–12쪽은 친숙한 설명, 시각 자료, 기존 한계와 설계 근거, 불필요한 내용 제거를 강조합니다.

| 처음 보는 분의 질문 | 설명·검토 방식 | 연결 자료 |
|---|---|---|
| 왜 필요한 연구인가? | 책의 내용과 기억이 다를 때 어느 쪽을 따를지 고르는 문제로 소개 | [README의 문제 설명](../README.md#왜-필요한가) |
| 기존 방식의 무엇이 부족한가? | 항상 개입하면 틀린 문맥의 영향은 줄여도 맞는 문맥의 답을 해칠 수 있음을 설명 | [외부 평가의 Always·Router 비교](research_status.md#3-외부-평가-routing과-packed) |
| 어떤 판단으로 설계했는가? | 내부 신호 → 개입하지 않기/유지/수용 → 답변의 개념도로 설명 | [방법 그림](../README.md#무엇을-연구하는가) · [연구 계획](research_plan.md) |
| 실제 근거는 무엇인가? | A1 CSV의 기준선·Always·Router 세 행과 신뢰구간을 확인 | [설치 없이 결과 읽기](getting_started.md#3-설치-없이-첫-결과-확인하기); 라이브 추론 시연과 구분 |
| 현재 한계는 무엇인가? | Packed의 올바른 문맥 손상, 미검증 결합, 비용·비교 조건을 함께 제시 | [결과와 한계](research_status.md) |

**짧은 설명 순서:** 문제 상황 → Always의 한계 → 선택적 개입 그림 → 결과 한 사례 → 실패 원인과 다음 검증입니다. 초기 로그인·웹·봇 시나리오나 실험 번호 전체 나열은 첫 설명에서 제외합니다. 발표자별 연습·시연 준비는 별도이며, 이 안내가 그 완료를 뜻하지 않습니다.

[제출용 프로젝트 정보와 8문장 소개](project_brief.md#제출용-프로젝트-정보)를 준비했습니다. 실제 수업 시스템 제출 여부는 저장소 정리와 별도로 확인합니다.

## 2. 공지 요구사항과 저장소의 대응

공지 2쪽은 **10/22 수업 대체로 10/21–10/26 중 팀 회의 및 회의록 작성**, **지금까지의 회의록과 개발 산출물(source code 등)이 포함된 팀 GitHub 주소 제출**, **10/26 제출 마감**을 안내합니다. 아래 표는 해당 요구와 자료 위치의 대응이며, 별도의 평가 배점표를 뜻하지 않습니다.

| 공지 요구 | 저장소에서 확인할 위치 | 확인 상태 |
|---|---|---|
| 자유 회의 기간의 회의록 | [10/22 팀 회의록](meeting-log/2026-10-22_회의록.md) | 안건·논의·결정·담당별 후속 과제 기록 |
| 지금까지의 회의록 | [날짜별 목록](README.md#회의와-원문-자료) · [원본 폴더](meeting-log/) | 기존 기록 보존; 요약보다 날짜별 원문 우선 |
| 개발 산출물·source code 포함 | [실험 코드](../experiments/README.md) · [공용 프롬프트·채점](../prompt/p8s_prompt.py) · [SOTA 코드 상태](../SOTA/README.md) | 코드와 일부 저장 결과 포함; 보고만 있는 결과와 구분 |
| 팀 GitHub 주소 제출 | [저장소](https://github.com/Ontology0/Graduation-Project) · [dev 명시 주소](https://github.com/Ontology0/Graduation-Project/tree/dev) | 저장소 준비와 수업 시스템 제출은 별개; 실제 제출 여부는 제출 내역에서 확인 |

10/27 확인 시 GitHub 기본 브랜치는 `dev`입니다. **이 안내의 정리일은 제출 마감 다음 날**이며, 10/27 추가 자료를 10/26 이전 제출물로 소급 표시하지 않습니다.

## 3. 지금까지의 활동 흐름

| 단계·기록 | 수행한 활동과 관찰 | 결정·다음 단계 | 연결된 개발 산출물 |
|---|---|---|---|
| Start 단계 | 지식–문맥 충돌 문제 정의, RAG 파이프라인·파일럿·데모 구성 | 초기 DPO/LoRA 구상과 이후 내부 신호 연구를 구분 | [초기 기록](archive/start-overview.md) · [이전 실험](../legacy/experiments/) · [RAG 구현](../src/) |
| 7월 실험 기록 | closed-book 응답과 entropy·confidence 등 기초 특성 분석 | 내부 표현에서 지식·문맥 신호를 읽는 방향으로 탐색 확장 | [exp5–7](../experiments/exp5-7/) · [7/11 결과 등록](https://github.com/Ontology0/Graduation-Project/commit/8f737e4) |
| [9/3](meeting-log/2026-09-03) · [9/8](meeting-log/2026-09-08_회의록.md) · [9/10](meeting-log/2026-09-10_회의록.md) | 학기 초 연구 계획·실험 진행과 팀 작업 논의 | 면담·팀 회의 기록을 이어가며 실험 구체화 | [P6](../experiments/P6/) · [P9](../experiments/P9/) · [P8S probe](../experiments/p8s_probe/) |
| [9/15](meeting-log/2026-09-15_회의록.md) · [9/22](meeting-log/2026-09-22_회의록.md) | 내부 표현 판독과 개입 이득 기반 선택 논의 | 상태 판독과 실제 행동 개선을 별도 평가 | [E2 층별·표면 정보 분석](../experiments/E2/) · [Steering 실험](../experiments/Steering_retain/) |
| [9/29 면담](meeting-log/2026-09-29_회의록.md) | head 단위 판독, 강한 개입의 C+ 손상, 스칼라 규칙의 한계 점검 | 판독 신호와 steering 방향 분리, 벡터 방향·동적 개입 검토 | [E13–E18 발표·선행 실험](../experiments/presentation/README.md) |
| [10/13 면담](meeting-log/2026-10-13_회의록.md) · [10/15 회의](meeting-log/2026-10-15_회의록.md) | Always 대비 Routing, One-pass와 분기 선택, 외부 비교 검토 | Routing 중심 후속 연구; 행동·강도·비용·선택 근거 분석 | [A0](../experiments/A0/) · [A1](../experiments/A1/) · [A3](../experiments/A3/) · [E17 Packed](../experiments/E17/) |
| [10/20 회의](meeting-log/2026-10-20_회의록.md) · [10/22 회의](meeting-log/2026-10-22_회의록.md) | 한이음 최종본 일정, 논문 리뷰 계획, 개발 산출물·회의록 정리 | 후속 실험 지속, 자료 누락 점검, 수업 제출 준비 | 아래 자유 회의 기간 기록 · [한이음 설계](han_eum_docs/hanium-design-v0.3.md) |
| [10/27 서면 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.xhbic2nnwq8w) | 외부 Router·Packed 비교와 C+ 손상 분석 보고 | 선택 규칙·외부 검증·공정 비교 보완 | [보고 수치와 조건](research_status.md) · [미완료 과제](research_plan.md) |

표의 코드 링크는 해당 논의와 관련된 현재 산출물입니다. **회의 날짜, 실험 수행일, GitHub 업로드 날짜는 동일하지 않을 수 있습니다.** 회의에서 제안한 일을 모두 완료한 것으로 해석하지 않습니다.

### 자유 회의 기간과 이후 정리 구분

| 구분 | 확인되는 기록 | 근거 |
|---|---|---|
| 10/21–10/26 기간 | 10/22 팀 회의록 등록 | [등록 커밋](https://github.com/Ontology0/Graduation-Project/commit/1f06c1a) · [회의록](meeting-log/2026-10-22_회의록.md) |
| 10/21–10/26 기간 | 10/22 P6/P9·E0/E1/E15/E17·Steering 등 기존 실험 파일 등록 | [업로드 커밋](https://github.com/Ontology0/Graduation-Project/commit/0660cb6); 일괄 등록일을 모든 실험의 수행일로 보지 않음 |
| 10/27 추가 정리 | A0/A1 코드·CSV·Parquet 등록, SOTA 파일 배치 정리 | [업로드 커밋](https://github.com/Ontology0/Graduation-Project/commit/5988255) |
| 10/27 추가 정리 | 발표 코드 연결, 연구 안내·활동 근거 정리 | [발표 코드](../experiments/presentation/README.md) · [원본 출처](../experiments/drive_sources.json); 기존 결과 정리이며 재실험 아님 |

## 4. 개발과 검증을 보여주는 대표 사례

| 질문 | 구현·산출물 | 확인된 것 | 남은 것 |
|---|---|---|---|
| 입력별로 개입을 고르면 항상 개입하는 것보다 좋은가? | [A1 노트북](../experiments/A1/A1_staged_routing.ipynb), [정책 CSV](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_policies.csv), [summary](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_summary.json) | P8S에서 Router의 Always 대비 +0.82%p, 95% CI [−0.49, +2.21]; 유의한 우위 미검출 | 저장 행동 결과를 이용한 정책 평가와 온라인 비용 검증을 구분 |
| 외부 데이터에서도 C+를 보호하는가? | [A3 노트북](../experiments/A3/A3_Always_Steering_External_Eval.ipynb), [외부 평가 보고](research_status.md#3-외부-평가-routing과-packed) | ConFiQA Router는 보고 조건에서 C+ 비열등 충족; Packed는 C+ 손상 관찰 | 표본 수·대상 라벨 학습 조건을 맞춘 비교, 원시 결과·실행본 대응 정리 |
| 한 prefill에서 두 정보원을 선택할 수 있는가? | [Packed 노트북](../experiments/E17/E17_packed.ipynb), [손상 진단](../experiments/E17/E17-0_Cplus_diagnosis.ipynb) | 문맥/closed-book 분기와 X1 선택 구현·분석 | 호출 1회를 동일 계산량으로 간주하지 않음; 외부 비용·선택 규칙 개선 |
| 기존 연구와 비교할 준비가 되었는가? | [SOTA 안내](../SOTA/README.md) | CAD/AdaCAD 코드와 비교 하네스 초안 | import 구조·stub 정리 필요; 완성된 SOTA 검증으로 주장하지 않음 |

저장소에 직접 저장된 결과, 외부 문서의 보고값, 앞으로 수행할 계획을 구분합니다. 실패·유의차 미검출·미구현 상태도 연구 진행의 근거로 함께 남깁니다.

## 5. 후속 일정과 공개 범위

공지 5쪽 기준 일정입니다. 이후 변경 공지가 나오면 별도로 갱신합니다.

| 예정일 | 수업 일정 | 연결할 준비 자료 |
|---|---|---|
| 11/3 | 포스터 발표 상세 공지 예정 | 상세 규격 확인 후 준비 범위 확정 |
| 11/17 | 포스터 발표 예정 | 연구 문제·핵심 관찰·현재 한계; [Project Brief](project_brief.md) |
| 12/1 | 졸업 발표(최종) | 핵심 기능 중심 시연, 비교 조건·성능·비용; [실험 안내](../experiments/README.md) |
| 12/8 | 완료보고서 제출 | 활동·개발·검증·팀 기여 근거를 연결한 최종 기록 |

공지 3쪽의 국내학술대회 지원 증빙은 투고·발표 사실 자료를 12/10까지 행정실에 제출하는 **별도 행정 절차**입니다. 이를 심사 중 논문·코드·결과를 공개 GitHub에 게시하라는 요구로 해석하지 않습니다. 현재 논문은 심사 중이며 게재·발표 완료로 표시하지 않습니다.

지식–문맥 4-state 판독 연구는 **[2026 한국소프트웨어종합학술대회(KSC 2026)](https://www.kiise.or.kr/conference/KSC/2026/)에 투고하여 심사 중**입니다. 투고 사실은 팀의 제출 기록에 근거하며, 학술대회 홈페이지 링크가 채택을 증명하는 것은 아닙니다.

회의록 원문과 기존 발표용 코드의 공개 범위는 유지합니다. 논문용 코드·결과를 다시 공개할지는 심사 및 제출처 규정 확인 후 결정합니다. [AI 활용·문서 정리 범위](ai_transparency_report.md)도 연구 수행 자체와 구분해 기록합니다.
