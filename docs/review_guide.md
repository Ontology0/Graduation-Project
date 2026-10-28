# 연구 활동과 주요 산출물

> 연구 기록: 2026-10-27 서면 보고까지 · 문서 업데이트: 2026-10-29

검색한 문서와 모델의 기존 지식이 충돌할 때, 어느 쪽을 활용해야 더 정확하게 답할 수 있을까요? Alltology는 모델 내부 신호를 분석하고, 입력에 따라 개입 여부·방향·강도를 선택하는 Routing과 내부 활성값을 조절하는 Steering을 연구합니다.

초기 RAG 구현에서 출발해 내부 신호 분석, 선택적 개입, 외부 벤치마크 검증으로 이어진 연구 활동과 산출물을 정리했습니다.

## 1. 처음 읽는 순서

| 순서 | 자료 | 살펴볼 내용 |
|---|---|---|
| ① 연구 이해 | [프로젝트 소개](project_brief.md) · [방법과 용어](getting_started.md) | 해결하려는 문제와 선택적 개입의 필요성 |
| ② 활동 흐름 | 아래 연구 경과 · [날짜별 회의록](README.md#회의와-원문-자료) | 관찰과 피드백이 다음 실험으로 이어진 과정 |
| ③ 코드와 결과 | [실험별 코드 지도](../experiments/README.md) · [주요 결과](research_status.md) | 구현한 방법, 비교 실험, 효과와 한계 |
| ④ 팀 활동 | [팀원별 활동](team_contributions.md) · [후속 연구](research_plan.md) | 연구 보고·코드·회의 기록과 다음 과제 |

실험을 실행하지 않아도 노트북과 저장된 결과를 읽을 수 있습니다. 첫 결과는 [A1 CSV 해설](getting_started.md#3-설치-없이-첫-결과-확인하기)에서 시작하고, 직접 실행할 때는 [입력과 환경 안내](../experiments/README.md#실행에-필요한-입력)를 참고하세요.

## 2. 지금까지의 연구 경과

| 단계·기록 | 수행한 활동과 관찰 | 결정·다음 단계 | 연결된 개발 산출물 |
|---|---|---|---|
| Start 단계 | 지식–문맥 충돌 문제 정의, RAG 파이프라인·파일럿·데모 구성 | 초기 DPO/LoRA 구상과 이후 내부 신호 연구를 구분 | [초기 기록](archive/start-overview.md) · [이전 실험](../legacy/experiments/) · [RAG 구현](../src/) |
| 7월 실험 기록 | closed-book 응답과 entropy·confidence 등 기초 특성 분석 | 내부 표현에서 지식·문맥 신호를 읽는 방향으로 탐색 확장 | [exp5–7](../experiments/exp5-7/) · [7/11 결과 등록](https://github.com/Ontology0/Graduation-Project/commit/8f737e4) |
| [9/3](meeting-log/2026-09-03) · [9/8](meeting-log/2026-09-08_회의록.md) · [9/10](meeting-log/2026-09-10_회의록.md) | 학기 초 연구 계획·실험 진행과 팀 작업 논의 | 면담·팀 회의 기록을 이어가며 실험 구체화 | [P6](../experiments/P6/) · [P9](../experiments/P9/) · [P8S probe](../experiments/p8s_probe/) |
| [9/15](meeting-log/2026-09-15_회의록.md) · [9/22](meeting-log/2026-09-22_회의록.md) | 내부 표현 판독과 개입 이득 기반 선택 논의 | 상태 판독과 실제 행동 개선을 별도 평가 | [E2 층별·표면 정보 분석](../experiments/E2/) · [Steering 실험](../experiments/Steering_retain/) |
| [9/29 면담](meeting-log/2026-09-29_회의록.md) | head 단위 판독, 강한 개입의 C+ 손상, 스칼라 규칙의 한계 점검 | 판독 신호와 steering 방향 분리, 벡터 방향·동적 개입 검토 | [E13–E18 발표·선행 실험](../experiments/presentation/README.md) |
| [10/13 면담](meeting-log/2026-10-13_회의록.md) · [10/15 회의](meeting-log/2026-10-15_회의록.md) | Always 대비 Routing, One-pass와 분기 선택, 외부 비교 검토 | Routing 중심 후속 연구; 행동·강도·비용·선택 근거 분석 | [A0](../experiments/A0/) · [A1](../experiments/A1/) · [A3](../experiments/A3/) · [E17 Packed](../experiments/E17/) |
| [10/20 회의](meeting-log/2026-10-20_회의록.md) · [10/22 회의](meeting-log/2026-10-22_회의록.md) | 한이음 최종본 일정, 논문 리뷰 계획, 개발 산출물·회의록 정리 | Routing·One-pass 후속 과제 지속, 팀원별 관련 논문 리뷰 계획 | [실험 코드](../experiments/README.md) · [한이음 설계](han_eum_docs/hanium-design-v0.3.md) |
| [10/27 서면 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.xhbic2nnwq8w) | 외부 Router·Packed 비교와 C+ 손상 분석 보고 | 선택 규칙·외부 검증·공정 비교 보완 | [보고 수치와 조건](research_status.md) · [미완료 과제](research_plan.md) |

각 단계의 회의록에는 당시 논의와 후속 과제가, 코드 링크에는 해당 주제의 현재 구현이 담겨 있습니다. 전체 회의 기록은 [날짜별 목록](README.md#회의와-원문-자료)에서 볼 수 있습니다.

## 3. 주요 구현과 실험 결과

평가에서는 전체 정답률과 함께 올바른 문맥(C+)에서의 성능을 살펴봅니다. 틀린 문맥의 영향을 줄이더라도, 맞는 문맥으로 답하던 능력을 잃는다면 개입 방식을 개선해야 하기 때문입니다.

| 연구 질문 | 구현·산출물 | 주요 관찰과 후속 과제 |
|---|---|---|
| 입력별 개입 선택이 항상 개입하는 것보다 좋은가? | [A1 노트북](../experiments/A1/A1_staged_routing.ipynb) · [정책 CSV](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_policies.csv) · [요약 결과](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_summary.json) | P8S의 저장 행동 결과를 이용한 정책 평가에서 Router는 Always 대비 +0.82%p였으나, 95% 신뢰구간 [−0.49, +2.21]로 유의한 우위는 확인되지 않았습니다. 온라인 추론 비용은 별도 검증 과제입니다. |
| 외부 데이터에서도 올바른 문맥의 답을 지킬 수 있는가? | [ConFiQA Router 실행본](https://drive.google.com/file/d/1ghpS2MP4XSeBh8R8t_Ay7KSN-o4PZcAG/view) · [외부 평가 보고](research_status.md#3-외부-평가-routing과-packed) | ConFiQA 1,000질문 보고에서 Router는 정답률 51.65% → 55.45%, C+ 성능 저하의 사전 허용 기준을 충족했습니다. 대상 데이터의 학습 fold 정답을 사용한 조건이며, NQ-Swap Router 평가는 후속 과제입니다. |
| 문맥과 자체 지식의 답변 분기를 비교하면 어떤가? | [Packed 노트북](../experiments/E17/E17_packed.ipynb) · [손상 진단](../experiments/E17/E17-0_Cplus_diagnosis.ipynb) · [외부 결과](research_status.md#3-외부-평가-routing과-packed) | 두 분기를 한 입력 처리 호출에 담고 선택하는 경로를 구현했습니다. 외부 보고에서 전체 정답률은 개선됐지만 올바른 문맥 대신 잘못된 자체 지식의 답을 고르는 손상이 나타나, 선택 규칙을 분석하고 있습니다. |
| 기존 방법과 어떻게 비교하는가? | [비교 코드 안내](../SOTA/README.md) | CAD/AdaCAD 코드와 비교 실행 도구 초안을 마련했습니다. 실행 구조 정비와 미구현 방법 추가 후 동일 조건의 비교 평가를 진행할 계획입니다. |

A1은 저장된 CSV·JSON 결과, 외부 평가는 팀 보고를 기준으로 정리했습니다. 표본·학습 조건·신뢰구간과 상세 분석은 [연구 결과](research_status.md), 온라인 개입과 내부 신호 분석 코드는 [발표·선행 실험](../experiments/presentation/README.md)에서 확인할 수 있습니다.

## 4. 팀 활동과 다음 연구

박세령·손현경·이다영이 팀 회의와 교수님 면담에서 연구 방향을 논의하고, 내부 신호 분석·Routing·Packed 실험을 진행해 왔습니다. [팀원별 활동](team_contributions.md)에서 회의록 작성, 연구 보고, 코드 공유 기록을 함께 볼 수 있습니다.

현재 후속 과제는 다음과 같습니다.

- 내부 신호와 행동·강도 선택의 관계를 분석하고 One-pass Routing을 고도화합니다.
- Packed가 올바른 문맥을 버리는 실패 원인을 분석하고 분기 선택 규칙을 개선합니다.
- 외부 벤치마크와 구성 요소별 비교를 확장하고, 정확도와 추론 비용을 함께 평가합니다.
- 별도로 구현한 Routing과 Packed의 결합 가능성을 검토합니다.

세부 연구 질문과 평가 방법은 [연구 계획](research_plan.md)에 정리했습니다.

## 5. 논문 투고 현황

내부 신호 분석에서 도출한 지식–문맥 4-state 판독 연구는 [2026 한국소프트웨어종합학술대회(KSC 2026)](https://www.kiise.or.kr/conference/KSC/2026/)에 투고하여 심사 중입니다. 논문용 코드와 상세 결과는 공개를 보류하고 있습니다.

[프로젝트 소개](project_brief.md) · [전체 회의록](meeting-log/) · [실험 코드](../experiments/README.md) · [팀원별 활동](team_contributions.md)
