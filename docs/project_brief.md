# 프로젝트 소개 — Alltology

> 2026-10-27 프로젝트 정보 취합용 · 팀원: 박세령, 손현경, 이다영 · 지도교수: 황의원

## 제출용 프로젝트 정보

| 항목 | 내용 |
|---|---|
| 트랙 | 연구 |
| 주제 | LLM의 지식–문맥 충돌에서 내부 신호 기반 선택적 개입 및 응답 전략 연구 |
| 키워드 | 지식 충돌, 내부 신호 분석, Activation Steering, Routing, 효율적 추론 |

## 프로젝트의 강점 및 특징

검색한 문서가 틀릴 수도, 모델이 기억한 정보가 틀릴 수도 있어, LLM이 어느 쪽을 따라야 하는지 상황별로 판단하는 기술이 필요합니다.
이를 위해 모델 내부 신호를 활용해 **개입 여부와 방향·강도를 선택하는 Routing**을 연구합니다.
특히 잘못된 문맥 때문에 생기는 오답을 줄이면서, 올바른 문맥으로 맞히던 답은 해치지 않는 것을 함께 목표로 합니다.
어텐션 헤드 등에서 내부 신호를 분석하고, 모델 가중치를 고정한 채 내부 활성값을 조절하는 Steering과 연결합니다.
단순히 상태를 잘 분류하는 데 그치지 않고, 개입했을 때 답변이 실제로 좋아지는지를 기준으로 선택 방법을 설계·검증합니다.
추론 중 행동을 결정하는 One-pass Routing과 문맥·자체 지식의 답변 분기를 비교하는 Packed 방식을 각각 구현·분석하며, 성능과 추론 비용을 함께 검토합니다.
자체 실험셋과 외부 벤치마크에서 비교 실험과 실패 원인 분석을 수행하여, 설계의 근거와 적용 범위를 확인합니다.
이와 별도로 내부 신호 분석에서 도출한 **지식–문맥 4-state 판독 연구는 2026 한국소프트웨어종합학술대회(KSC 2026)에 투고하여 현재 심사 중**입니다.

## 소개문을 뒷받침하는 자료

| 소개의 핵심 | 근거 | 과장하지 않을 범위 |
|---|---|---|
| 왜 선택적 개입인가? | [10/13 면담](meeting-log/2026-10-13_회의록.md), [10/15 결정](meeting-log/2026-10-15_회의록.md), [외부 평가](research_status.md#3-외부-평가-routing과-packed) | 항상 개입할 때의 손상에서 출발; 모든 데이터에서 해결됐다는 주장은 아님 |
| 상태 분류보다 개입 이득을 평가 | [A0](../experiments/A0/), [A1 정책·결과](../experiments/A1/%5Bresult%5DA1_staged_routing/) | P8S Router의 Always 대비 유의한 우위는 미검출 |
| 내부 신호·온라인 개입·후보 선택 | [온라인 Router](../experiments/presentation/E15_Online_StrongRetain_UtilityRouter.ipynb), [E17 Packed](../experiments/E17/E17_packed.ipynb) | 별도 구현·분석이며 결합 성능·보편적 속도 개선은 미검증 |
| 외부 비교·실패 분석 | [다영 Router 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.ip6i2nm6wvrb), [현경 Packed 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.6grhiq4uqc72) | Router의 대상 라벨 학습과 Packed의 대상 라벨 미사용을 구분; Packed의 C+ 손상은 미해결 |
| 별도 학술 성과 | [10/15 제출 기록](meeting-log/2026-10-15_회의록.md), [KSC 2026](https://www.kiise.or.kr/conference/KSC/2026/) | 투고·심사 중이며 게재·발표 미확정; 논문용 상세 자료 공개 보류 |

모델 가중치 고정은 Router·판독기의 별도 학습까지 없다는 뜻이 아닙니다. 개입 위치와 신호를 읽는 위치도 실험마다 다르므로, 모든 방법을 어텐션 헤드 직접 조작으로 묶지 않습니다.

[처음 읽는 안내](getting_started.md) · [교수님 검토 안내](review_guide.md) · [결과·조건·한계](research_status.md)
