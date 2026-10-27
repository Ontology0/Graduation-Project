# 기말발표용 코드와 선행 실험

> 2026-10-27에 [공유 Drive 폴더](https://drive.google.com/drive/folders/1F3Hk6TE6pbJ6TIz1hiQaoJerlQxdHr8Y)에서 가져온 발표·연구 흐름용 묶음입니다. 같은 폴더의 [논문 심사용 코드](../paper/README.md)는 별도로 정리했습니다.

폴더 안의 실험을 모두 최종 채택 방법으로 보지는 않습니다. 판독, 규칙, 실제 개입을 비교한 선행·후속 실험을 함께 보존합니다. 발표 E16의 20% 재현과 20%·80% 비교 코드는 중복 복사하지 않고 [논문 폴더의 E16_role_20_80.ipynb](../paper/E16_role_20_80.ipynb)에 연결합니다.

## 코드 읽는 순서

| 코드 | 연구에서의 역할 |
|---|---|
| [E13_ProbeAttribution_CausalSparseGate.ipynb](E13_ProbeAttribution_CausalSparseGate.ipynb) | Probe에 관련된 구성요소 분석, ablation·patching과 sparse gate 검증 |
| [E14_L13_HeadDissection_5Fold.ipynb](E14_L13_HeadDissection_5Fold.ipynb) | L13 헤드 선별·판독과 질문 단위 5-fold 평가 |
| [E14_L13_HeadDissection_5Fold_plus_router_metrics.ipynb](E14_L13_HeadDissection_5Fold_plus_router_metrics.ipynb) | E14에 routing 관련 진단 지표를 추가한 버전 |
| [E15_Online_StrongRetain_UtilityRouter.ipynb](E15_Online_StrongRetain_UtilityRouter.ipynb) | 실제 forward 중 L13 신호를 읽고 L14–18 개입·생성을 수행하는 이득 예측 Router |
| [E16_LowLabel_E14_ProbeFree_State.ipynb](E16_LowLabel_E14_ProbeFree_State.ipynb) | 소량 라벨로 head/sign을 고정한 뒤 규칙 판독과 지도학습 LR 판독을 분리 비교 |
| [E17_FixedGeometry_5Fold.ipynb](E17_FixedGeometry_5Fold.ipynb) | 같은 head·split·steering 아래 scalar/vector/방향/prototype 판독 비교 |
| [E18A_EarlyK_LateC_4State_5Fold.ipynb](E18A_EarlyK_LateC_4State_5Fold.ipynb) | K/C의 판독 층·위치·분류 구조를 나누는 진단 실험 |
| [E18B_Readable_5Fold.ipynb](E18B_Readable_5Fold.ipynb) | C 판독을 고정하고 질문 위치의 다층 K와 L13 K를 비교 |

**번호만으로 기존 실험과 합치지 않습니다.** 여기의 `E17_FixedGeometry`는 [E17 Packed](../E17/E17_packed.ipynb)와 다른 방법이며, `E15_Online_StrongRetain`도 [E15 C-proxy gate](../E15/E15_cproxy_gate.ipynb)와 별개입니다. Q→C 계열의 EM을 A1의 C→Q 결과와 동일 조건으로 비교하지 않습니다.

## 현재 Routing·Packed 연구와 연결

- 저장된 행동 결과를 이용하는 정책 평가: [A0](../A0/) · [A1](../A1/)
- Always Steering 외부 평가·강도 탐색: [A3](../A3/)
- Packed 개발·C+ 손상 진단: [E17](../E17/)
- 별도 Drive의 ConFiQA Router 실행본: [ext_router_confiqa.ipynb](https://drive.google.com/file/d/1ghpS2MP4XSeBh8R8t_Ay7KSN-o4PZcAG/view) · [공유 폴더](https://drive.google.com/drive/folders/1aNJs2fz8VOuqjkUDFikbMdEIsj1Sld22)

외부 ConFiQA Router 실행본은 존재하며 위에 연결했습니다. 이번 가져오기 대상 폴더의 노트북과는 별도입니다. 외부 결과는 [연구 결과와 근거](../../docs/research_status.md)의 표본 수·라벨 사용 조건을 따라 읽습니다.

## 실행과 원본

- GPU 노트북은 모델 접근 권한과 선행 E11/E14·P8S 입력이 필요합니다. 설치·Drive 경로·모델 revision·cache 조건은 각 노트북에서 확인합니다.
- 노트북의 코드·설명은 원문 그대로이며, 출력·실행 횟수·실행자 메타데이터만 제거했습니다. 원문 설명의 실행 상태·수치는 작성 당시 기록입니다. 이번 정리에서 학습이나 GPU 실험을 재실행하지 않았습니다.
- 파일별 Drive 원본·수정 시각은 [출처 목록](../drive_sources.json)에 있습니다. 저장 출력이 필요하면 해당 원본을 열어 확인합니다.
- [E18A 결과 ZIP](https://drive.google.com/file/d/16gsGWwRrFwTs-vg_v7qRf28eEW6PhERy/view)과 [E18B 설계 HTML](https://drive.google.com/file/d/1fpdTrEISZiixrEHpDXRtAgBx6HpaEfRO/view)은 원본 링크로 제공합니다.

[논문 심사용 코드](../paper/README.md) · [전체 실험 안내](../README.md)
