# 논문 심사용 코드

> 2026-10-27에 [공유 Drive 폴더](https://drive.google.com/drive/folders/1F3Hk6TE6pbJ6TIz1hiQaoJerlQxdHr8Y)에서 가져온 코드입니다. [기말발표·선행 실험](../presentation/README.md)과 구분합니다.

## 먼저 볼 실행본

| 코드 | 용도 | 환경·결과 |
|---|---|---|
| [E16_review_v10.ipynb](E16_review_v10.ipynb) | 논문 심사 대응: 역할별/전체 헤드/블록 표현, 내부 CV, 역할 ablation, K집단별 C 판독, 문맥 TF-IDF | scikit-learn **1.8.0** · [저장 결과](results/review_v10/) |
| [E16_role_20_80.ipynb](E16_role_20_80.ipynb) | 발표 E16의 역할별 헤드 판독 재현, 공통 평가셋에서 20%·80% 라벨 예산 비교 | scikit-learn **1.6.1** · [저장 결과](results/role_20_80/) |

둘은 각각 새 런타임에서 실행합니다. 역할별 top-4 합집합의 마지막 위치 벡터를 LR로 판독하며, seed 42–46의 반복 홀드아웃입니다. 5-fold OOF나 실제 QA 개선 실험으로 해석하지 않습니다.

## 논문 표와 결과 파일의 대응

| 항목 | 저장 파일·조건 |
|---|---|
| 평가 A 역할별 헤드 Macro-F1 **0.6123 ± 0.0121** | [review SUMMARY.csv](results/review_v10/SUMMARY.csv), `panel=A`, `budget=0.2`, `method=role_fixed` |
| 내부 CV 역할별 헤드 **0.6165 ± 0.0152**, 전체 32헤드·블록 비교 | 같은 `SUMMARY.csv`의 `role_tuned`, `all32_*`, `full_hidden_*` |
| 고정 정규화 무작위 헤드 **0.5961 ± 0.0086** | [role PAPER_SUMMARY.csv](results/role_20_80/PAPER_SUMMARY.csv), `E16_source20_test80`, `random_union_LR`; REVIEW 실행과 구분 |
| K/C AUROC, K−에서 C AUROC | [review SUMMARY.csv](results/review_v10/SUMMARY.csv), [C_AUC_BY_K.csv](results/review_v10/C_AUC_BY_K.csv) |
| 문맥만 읽는 기준선 | [TEXT_AUC_BY_K.csv](results/review_v10/TEXT_AUC_BY_K.csv) |
| 방법 간 대응 차이·신뢰구간 | [PAIRED_CI.csv](results/review_v10/PAIRED_CI.csv) |
| 발표 E16 **0.6120 ± 0.0123** | [role PAPER_SUMMARY.csv](results/role_20_80/PAPER_SUMMARY.csv), `E16_source20_test80`, `diagnostic_same_roleheads_LR` |

**발표와 심사용 논문은 실행 버전·환경이 다릅니다.** 위 수치는 Drive CSV를 대조한 값이며 이번 가져오기에서 재학습하지 않았습니다. 차이를 전부 라이브러리 버전 때문이라고 단정하지 않습니다. 실제 실행 환경은 각각의 [ROLE ENVIRONMENT.json](results/role_20_80/ENVIRONMENT.json)과 [REVIEW ENVIRONMENT.json](results/review_v10/ENVIRONMENT.json)을 확인하세요.

전체 결과·예측·감사 기록은 [ROLE 실행 폴더](https://drive.google.com/drive/folders/16ZjA-fB4MbOpjr8WMtQ6oqoaCwa6GVyY)와 [REVIEW 실행 폴더](https://drive.google.com/drive/folders/1JAahBUtTtDuSBeTMdp1Hf75V_NKvbssg)에 있습니다. 저장소에는 작은 집계 CSV와 환경 기록만 복사했습니다.

## 실행 전 준비

1. Colab/Jupyter의 새 런타임에서 선택한 노트북의 설치 셀부터 실행합니다. 서로 다른 scikit-learn 환경을 섞지 않습니다.
2. 기본 CPU 분석에는 `p8s_behavior_v2.csv`와 `L13_neutral_head_bank_all_rows.npz`가 필요합니다. 노트북의 Drive 파일 ID와 SHA-256 검사를 유지합니다. 입력 접근 실패를 다른 데이터로 대체하지 않습니다.
3. Colab에서는 Drive를 연결하고 `MyDrive/p8s`의 출력 경로를 확인합니다. 실행마다 별도 결과 폴더가 만들어집니다.
4. REVIEW의 선택 GPU 검증은 기본적으로 꺼져 있습니다. 켜려면 모델 접근 권한·GPU·추가 의존성이 필요하며, 기본 CPU 결과와 구분합니다.
5. 20%는 해당 분할의 선별·학습 라벨 예산입니다. 선행 설계 탐색의 라벨 사용이나 독립 외부 평가를 뜻하지 않습니다.

## 추가 통제 실험

| 코드 | 위치와 한계 |
|---|---|
| [KSC_control_fresh_v3.ipynb](supporting/KSC_control_fresh_v3.ipynb) | E14의 가변-k 선택 경로를 유지한 새 학습 전용 통제 실험 |
| [KSC_control_context_v2.ipynb](supporting/KSC_control_context_v2.ipynb) | 같은 통제 실험의 앞선 연구 맥락 설명본 |

이 통제 실험은 E16 역할별 top-4 경로와 다릅니다. 통제 실험의 0.5914를 논문 역할별 판독의 수정값으로 사용하지 않습니다.

## 가져오기 범위

셀의 코드·설명은 원문을 유지하고 실행 출력·실행 횟수·실행자 메타데이터를 제거했습니다. 원문 설명 중 ‘저장 출력’은 Drive 원본을 가리키며, 이 저장소의 노트북 출력은 비어 있습니다. 파일별 원본 URL·수정 시각은 [출처 목록](../drive_sources.json)에 기록했습니다. Drive 원본과 공유 설정은 변경하지 않았습니다.

[연구 결과와 한계](../../docs/research_status.md) · [전체 실험 안내](../README.md)
