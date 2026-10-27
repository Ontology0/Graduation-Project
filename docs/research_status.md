# 연구 결과와 근거

> 업데이트: 2026-10-27. 제공된 발표·교수님 미팅 자료와 저장소 `5988255` 시점의 실험 산출물을 대조한 문서입니다. 수치는 해당 자료의 보고값이며 이번 정리에서 모델을 재실행하지 않았습니다.

## 출처와 읽는 순서

| 출처 | 버전·위치 | 이 문서에서 사용하는 범위 |
|---|---|---|
| 교수님 미팅 자료, Google Docs | [13회차 10/13](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.5k7e1omlwoie), [14회차 10/27](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.xhbic2nnwq8w) | 방법별 조건, 외부 평가와 후속 과제 |
| `졸업프로젝트 교수님 미팅 자료 (6).pdf` | 사용자 제공 289쪽 스냅샷 | A3·Routing·Packed 보고와 연구 흐름 대조 |
| `alltology_presentation (2).pdf` | 사용자 제공 58쪽, 특히 39·40·47·53쪽 | 판독과 응답 개선의 구분, 이전 E14/E16 평가 설명 |
| A0/A1 저장 산출물 | [A0 summary](../experiments/A0/%5Bresult%5DA0_headroom/A0_summary.json), [A1 policies](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_policies.csv), [A1 summary](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_summary.json) | P8S 행동·정책 결과와 oracle/실행 가능한 정책 구분 |
| 공유 Drive 발표 코드 | [발표 코드](../experiments/presentation/README.md), [원본 목록](../experiments/drive_sources.json) | 공개된 발표·선행 실험 노트북 8개 |
| 날짜별 회의록 | [10/15](meeting-log/2026-10-15_회의록.md), [10/22](meeting-log/2026-10-22_회의록.md) | Routing 중심 연구 방향과 후속 작업 |

PDF 원본은 이 저장소에 추가하지 않았습니다. Google Docs 원문은 접근 권한이 필요할 수 있으며, 위 제목·쪽수와 아래 요약으로 자료 버전을 구분합니다.

## 1. 지식–문맥 4-state 판독

문맥 없는 응답의 정오(K)와 문맥의 정오(C)를 내부 표현에서 판독하는 연구입니다. 상태 판독과 실제 답변 개선은 구분합니다.

관련 논문은 심사 중이며, 논문용 코드·결과 파일·세부 수치는 공개를 보류합니다. 기존 [발표·선행 실험 코드](../experiments/presentation/README.md)는 유지하며, 논문의 공개 범위는 심사 및 제출처 규정 확인 후 별도로 결정합니다.

## 2. P8S: Always Steering과 Routing

[A1 policies CSV](../experiments/A1/%5Bresult%5DA1_staged_routing/A1_policies.csv)의 612질문·1,224입력 결과입니다. EM은 %, 변화는 %p로 표시합니다.

| 정책 | 전체 EM | Base 대비 ΔEM | C− ΔEM | C+ ΔEM | Always 대비 ΔEM [95% CI] |
|---|---:|---:|---:|---:|---:|
| No-op / Base | 53.10 | — | — | — | — |
| Always retain, late ρ=0.06 | 59.97 | +6.86 | +13.56 | +0.16 | 기준 |
| Late-only L13, 이득 예측 | 60.78 | +7.68 | +14.54 | +0.82 | +0.82 [−0.49, +2.21] |
| Staged L7→L13, 이득 예측 | 60.78 | +7.68 | +14.54 | +0.82 | +0.82 [−0.49, +2.21] |

현재 P8S 설정에서 Router의 Always 대비 유의한 우위는 검출되지 않았습니다. A1은 저장된 hidden과 행동별 생성 결과를 이용한 정책 평가이며, 온라인 통합 추론의 지연 측정과 구분합니다. Oracle 결과는 정답 행동을 아는 상한으로, 실행 가능한 방법의 성능에 포함하지 않습니다.

10/13·10/27 보고의 packed P8S EM은 **66.01%**, seed 0/1/2 평균입니다. 이는 설계에 사용한 개발셋 결과이며, A1 CSV와는 생성 조건·baseline 차이를 확인해야 하므로 이 문서에서 두 산출물을 합쳐 새로운 paired 검정을 계산하지 않습니다.

## 3. 외부 평가: Routing과 Packed

원문: [10/13 Always·Routing 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.ip6i2nm6wvrb), [10/27 통합 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.xhbic2nnwq8w), [Packed 상세](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.6grhiq4uqc72).

### 공통 조건과 차이

- C+·C− 모두 **원래 사실 정답**으로 채점합니다. 변조된 문맥을 따르는 과제의 원 논문 점수와 직접 비교하지 않습니다.
- 개선: 전체 ΔEM의 95% CI 하한 > 0. C+ 비열등: C+ ΔEM의 95% CI 하한 > −2%p
- 신뢰구간: 질문 단위 bootstrap 2,000회; 같은 질문의 C± 쌍 유지
- Router: P8S steering 방향 전이 + **대상 ConFiQA train fold의 정답으로 이득 회귀 학습**, 질문 단위 outer 5-fold·inner 4-split
- Packed: P8S에서 사양 고정, 대상 데이터 라벨 없이 온라인 방향 갱신·X1 분기 선택, seed 0/1/2 평균
- 아래 외부 수치는 보고 문서 기준입니다. 공개된 A0/A1 결과 CSV는 P8S용이며 외부 결과의 원시 행별 파일을 대신하지 않습니다.

### ConFiQA-QA: 1,000질문 / 2,000입력

| 방법 | EM (%) | ΔEM [95% CI], %p | C+ Δ [CI 하한], %p | C− Δ, %p | C+ 비열등 |
|---|---:|---:|---:|---:|---|
| Base | 51.65 | — | — | — | — |
| Always ρ=0.06 | 54.30 | +2.65 [1.35, 3.90] | −2.90 [−4.50] | +8.20 | 미충족 |
| Router | 55.45 | +3.80 [2.70, 5.05] | +0.80 [−0.60] | +6.80 | 충족 |
| Packed | 55.80 | +4.15 [2.52, 5.90] | −7.60 [−9.50] | +15.90 | 미충족 |

Router − Always는 +1.15%p [0.10, 2.20]로 개선이 관측됐습니다. Packed − Router는 +0.35%p [−1.27, 1.93]로 우위가 검출되지 않았습니다. Router의 C+ **비열등 충족은 C+ 개선 입증과 다릅니다**.

### NQ-Swap: 표본 크기를 구분

| 표본 | 방법 | EM (%) | Base 대비 ΔEM [95% CI], %p | C+ Δ [CI 하한], %p |
|---|---|---:|---:|---:|
| 1,000질문 | Base | 45.75 | — | — |
| 1,000질문 | Packed | 51.97 | +6.22 [4.31, 8.04] | −8.50 [−10.52] |
| 공통 300질문 | Base | 47.83 | — | — |
| 공통 300질문 | Always ρ=0.06 | 50.17 | +2.34 [−0.48, 4.95] | −5.00 [−8.39] |
| 공통 300질문 | Packed | 51.00 | +3.17 [−0.32, 6.57] | −10.22 [−14.30] |

300질문의 Packed − Always는 +0.83%p [−1.91, 3.54]로 유의한 차이가 검출되지 않았습니다. **1,000질문 Packed와 300질문 Always의 EM을 직접 순위 비교하지 않습니다.** NQ-Swap Router는 10/27 보고 기준 미실시입니다.

### Packed의 구조와 실패 관찰

문맥 A와 closed-book B를 한 시퀀스에 넣되 attention mask·위치 번호로 B를 격리합니다. A에만 L14–18, ρ=0.04 steering을 적용하고, 이전 묶음의 hidden으로 `w_ctx−`를 누적합니다.

X1은 첫 토큰이 다르고 `log P_A(top1_B) > log P_B(top1_A)`이면 B를 선택하고, 아니면 A를 선택합니다. **이는 Router의 행동별 이득 예측과 다른 규칙**입니다. 둘을 결합한 결과는 아직 없습니다.

외부 데이터에서는 이득이 K+C−, 손실이 K−C+에 집중됐습니다. Steering 없는 X1에서도 C+ 손상이 나타나, 방향 강도만 낮추는 것으로는 해결되지 않았습니다. 다만 손실 표본 20개의 1인 audit에서는 9개가 채점·데이터 문제로 분류됐으므로, 해당 비율을 전체 손실로 일반화하거나 packed만 보정하지 않습니다.

P8S의 지연 1.09배·prefill 토큰 약 39% 증가는 기존 E17 측정값입니다. 외부 평가의 재측정 비용 또는 모든 환경의 속도 보장으로 사용하지 않습니다.

## 4. A3는 별도 실험

[A3·A3-1 보고](https://docs.google.com/document/d/1Vtvi7ep749i36YIoLx4nPc7nyiawetBDexZ_sst6XEQ/edit?tab=t.naiwhgc68vcw)는 외부 데이터 **각 1,200질문**, Always Steering A0 ρ=0.06의 실험입니다.

| 데이터 | Base EM (%) | A0 EM (%) | 전체 ΔEM (%p) | C+ ΔEM (%p) | C− ΔEM (%p) |
|---|---:|---:|---:|---:|---:|
| P8S, 612질문 | 53.10 | 60.05 | +6.94 | +0.33 | +13.56 |
| NQ-Swap, 1,200질문 | 45.38 | 49.96 | +4.58 | −3.08 | +12.25 |
| ConFiQA-QA, 1,200질문 | 51.13 | 54.42 | +3.29 | −3.00 | +9.58 |

변화량은 원문 보고값이며 표시된 반올림 EM의 차이와 마지막 자릿수가 다를 수 있습니다. 외부 두 데이터에서 전체·C− 개선은 관측됐으나 C+ 비열등은 미충족입니다. A3-1은 결과 확인 후의 강도 sweep와 C− 비율 재가중 탐색이며, 새 강도의 확증 실험이 아닙니다.

위 표를 1,000질문 Router·Packed 평가와 합치지 않습니다. A3 노트북의 초기 “QA 미측정” 문구와 이후 보고서의 결과가 다르므로, **코드 파일의 설명 시점과 보고 수치의 시점도 구분**해야 합니다.

## 5. 공개 상태와 다음 확인

| 항목 | 현재 확인 가능한 것 | 남은 것 |
|---|---|---|
| P8S probe | 노트북·CSV | 선행 원본·hidden 생성 환경 준비 |
| A0/A1 | 노트북·행동별 Parquet·정책 CSV | P9 공유 입력과 연결, 온라인 실행 비용 검증 |
| A3 | 외부 평가·강도 분석 노트북, 문서 보고값 | 보고값과 연결된 원시 결과 공개 |
| 외부 ConFiQA Router | [Drive 실행본](https://drive.google.com/file/d/1ghpS2MP4XSeBh8R8t_Ay7KSN-o4PZcAG/view), 문서 보고값 | 실행 입력·행별 결과·manifest와 보고 표의 대응 정리 |
| E17 | packed 개발·진단 노트북, 외부 보고값 | 외부 실행본·결과 manifest 연결 |
| 4-state 논문 | 심사 중; 논문용 코드·결과 공개 보류 | 심사 및 제출처 규정 확인 후 공개 범위 결정 |
| SOTA 하네스 | CAD/AdaCAD 코드·여러 방법의 stub | 패키지 구조 정리, 미구현 방법·외부 평가 연결 |

현재 핵심 결론은 **상태를 읽을 수 있다는 것과 좋은 답을 선택할 수 있다는 것은 다르다**는 점입니다. Router는 라벨 학습 조건에서 C+ 손상을 줄였고, packed는 대상 라벨 없이 큰 C− 이득을 얻었지만 외부 C+ 보호에 실패했습니다. 최종 방법·결합 방식·SOTA 우위는 아직 확정하지 않습니다.
