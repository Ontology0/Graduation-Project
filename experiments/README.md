# 실험 안내

> 업데이트: 2026-10-27 · GitHub `5988255`까지의 업로드 반영. 최신 보고 수치는 [연구 결과와 근거](../docs/research_status.md)를 참고하세요.

회의에서 정한 과제가 어떤 코드·결과로 이어졌는지는 [교수님 검토 안내](../docs/review_guide.md)에서 확인할 수 있습니다. GitHub 업로드 날짜와 실제 실험 수행일은 구분합니다.

## 제출 목적별 코드

기말발표·선행 실험 노트북 8개를 공개합니다. 논문용 코드·결과는 심사 중이므로 공개를 보류하며, 기존 실험 경로는 옮기지 않았습니다.

| 묶음 | 내용 |
|---|---|
| [기말발표용·선행 실험](presentation/README.md) | E13–E18 판독·개입 노트북 8개, 현재 Routing·Packed 실험 연결 |

원본 코드 셀은 유지하고 출력·실행자 메타데이터를 제거했습니다. [출처 목록](drive_sources.json)에 원본 URL과 수정 시각을 기록했습니다. 이번 가져오기에서 모델을 재실행하지 않았습니다.

## 현재 연구를 읽는 순서

**프롬프트·라벨 검증 → 내부 신호 판독 → steering → 행동 선택 / 후보 선택 → 외부 평가** 순서로 읽으면 연구 흐름을 이해하기 쉽습니다. 모든 노트북을 순서대로 실행하는 하나의 파이프라인은 아닙니다.

| 실험 | 목적 | 코드·산출물 |
|---|---|---|
| [E0](E0/E0_prompt_bias.ipynb) | 프롬프트 지시·few-shot이 응답 선택에 주는 편향 | 프롬프트 비교 노트북 |
| [E1](E1/E1a_hook_relabel.ipynb) | hidden 추출·hook·K 라벨 재판정 | 선행 데이터 생성·점검 노트북 |
| [P8S probe](p8s_probe/p8s_probe.ipynb) | Q↔CQ 전이, 같은 prefill에서 K 판독 가능성 | [CSV·프로파일](p8s_probe/result/) |
| [E2a](E2/E2a_layer_probe_v2_0-based.ipynb) · [E2b](E2/E2b_surface_vs_knowledge_p8s_v2.ipynb) | 층별 K/C 신호와 질문 표면 정보 통제 | CPU 분석 노트북 |
| [P9](P9/) | steering 방향·레이어·생성 길이·채점·재현성 발전 | 파일럿부터 P9v4까지 노트북 |
| [Steering_retain](Steering_retain/) | PKS·steering 및 강도·routing 후속 분석 | [개발본](Steering_retain/Steering_develop.ipynb), [강도·routing](Steering_retain/P9v4_strength_routing.ipynb) 등 |
| [E15](E15/E15_cproxy_gate.ipynb) | 내부 C-proxy gate와 head 개입의 효과·한계 | 탐색·검증 노트북 |
| [A0](A0/A0_headroom_check.ipynb) | 행동 집합과 개입 선택의 개선 여지 | [행동별 Parquet·CSV·summary](A0/%5Bresult%5DA0_headroom/) |
| [A1](A1/A1_staged_routing.ipynb) | early/late/staged routing, 상태 예측과 이득 예측 비교 | [정책 CSV·선택 결과](A1/%5Bresult%5DA1_staged_routing/) |
| [A3 외부 평가](A3/A3_Always_Steering_External_Eval.ipynb) | Always Steering의 P8S·NQ-Swap·ConFiQA-QA 전이 | 평가 코드, 결과는 미팅 보고에 정리 |
| [A3-1](A3/A3-1_Strength_and_Mixture.ipynb) | 개입 강도와 C− 비율별 이득·손상 | 후속 탐색 코드 |
| [E17 진단](E17/E17-0_Cplus_diagnosis.ipynb) · [Packed](E17/E17_packed.ipynb) | C+ 보호·강도 상한 분석, 문맥/closed-book 분기 선택 | 개발·ablation·온라인 packed 노트북 |
| [SOTA 하네스](../SOTA/README.md) | 동일 조건에서 기준선·기존 방법 비교 | Python 초안; 패키지 구조·외부 입력 정리 필요 |

### 앞선 탐색

[exp5-7](exp5-7/)은 데이터 구조·entropy·confidence, [P6](P6/)는 다중 데이터 수집·clustering·교정·시각화 단계입니다. 5~7월 파일럿과 이전 결과는 [legacy/experiments](../legacy/experiments/) 및 [legacy/outputs](../legacy/outputs/)에 있습니다.

## 무엇을 바로 확인할 수 있나?

GPU 없이 읽을 수 있는 결과부터 확인하세요.

- [P8S cross-input 결과](p8s_probe/result/cross_transfer_results.csv)
- [A0 summary](A0/%5Bresult%5DA0_headroom/A0_summary.json) — oracle 상한과 행동 집합의 한계
- [A1 policies](A1/%5Bresult%5DA1_staged_routing/A1_policies.csv) — Base 0.5310, Always 0.5997, late gain Router 0.6078
- [A1 summary](A1/%5Bresult%5DA1_staged_routing/A1_summary.json) — Router − Always +0.82%p [−0.49, +2.21], 유의차 미검출

이 CSV는 **P8S** 결과입니다. 문서의 ConFiQA·NQ-Swap 외부 결과 또는 논문 최종 표를 이 파일에서 재생성할 수 있다고 가정하지 않습니다.

## 실행에 필요한 입력

| 경로 | 필요 입력·환경 | 실행 범위 |
|---|---|---|
| P8S probe | `p8s_pairs.csv`, 모델 접근 권한, GPU | hidden 추출·probe 평가 |
| E2 | `new_data/`의 hidden·라벨·행 정렬용 데이터, CPU | 기존 cache 분석 |
| P9 / E0 / E1 / E15 / E17 | 각 셀의 Drive 경로·선행 P9 산출물, 모델·GPU | 노트북별로 환경·실행 순서 확인 |
| A0 | P9 hidden·steering·manifest 입력, GPU | 행동별 생성 결과 구성 |
| A1 | A0 행동 결과, P9 hidden·라벨·manifest, CPU | 저장된 결과를 이용한 정책 평가 |
| A3 / A3-1 | P8S 방향 추정 자료·외부 데이터, GPU; A3-1은 기존 A3 산출물 | 별도 외부 평가·강도 탐색 |
| SOTA | P9 입력·A0 결과·프롬프트 hash·환경, 패키지 구조 복원 | 현재는 완성된 실행 패키지가 아님 |

원본 CSV·대형 hidden cache·일부 manifest는 별도 공유 자료입니다. 저장소의 결과 Parquet만으로 모든 선행 입력이 충족되지는 않습니다. 설치는 해당 노트북의 셀을 기준으로 하고, 요구 시 런타임을 재시작합니다. 루트 `requirements.txt`는 초기 RAG용입니다.

## 비교할 때 고정할 것

1. **질문 단위 분할:** 같은 질문의 C±를 학습과 평가에 나누지 않습니다.
2. **K 라벨:** strict EM, relaxed/audit, `kside_v3`, 논문 교정 라벨을 구분합니다. 612질문이어도 K+ 개수가 다를 수 있습니다.
3. **레이어 번호:** P8S probe 배열은 index 0에 embedding을 포함합니다. E2a는 embedding 없는 decoder 출력과 0-based 번호입니다.
4. **프롬프트·생성:** [공용 모듈](../prompt/p8s_prompt.py)은 `p8s-v2`, 최대 192토큰입니다. 과거 노트북의 48토큰 설정을 최신 기준선과 섞지 않습니다.
5. **행 정렬과 환경:** row manifest, prompt hash, model revision, 배치 구성, seed/fold, 채점 함수를 결과와 함께 기록합니다.
6. **지표와 oracle:** 상태 Macro-F1·AUROC, QA EM/F1, 실제 추론 비용은 각각 보고합니다. Oracle은 달성 가능한 runtime 방법이 아닙니다.
7. **외부 채점:** C± 모두 사실 정답으로 채점한 결과는 원 벤치마크의 context-faithfulness 점수와 직접 비교하지 않습니다.

## 아직 연결해야 할 산출물

- 심사 중인 논문의 실행본·환경·집계 결과는 공개 보류입니다.
- ConFiQA Router 실행본은 [발표 코드 안내](presentation/README.md)에 연결했습니다. 외부 Router·Packed 보고와 원시 행별 결과·manifest의 대응은 추가 정리가 필요합니다.
- A3 문서 보고값과 결과 폴더의 대응
- SOTA 하네스의 package 배치·미구현 방법·외부 벤치마크
- Router와 packed를 실제로 결합한 구현·평가

[연구 계획](../docs/research_plan.md) · [자료별 결과와 한계](../docs/research_status.md)
