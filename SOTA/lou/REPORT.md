# Lou et al. (arXiv 2610.20067) SOTA 재현 결과 보고 — NQ-Swap · Llama-3.1-8B-Instruct

> 작성일: 2026-11-26 · 작업 브랜치: `sota/lou` · 폴더: `SOTA/lou/`

## 1. 요약

- 공개 코드(upstream, commit `48148da`)를 수정 없이 실행해 논문 Table 1의 NQ-Swap · Llama 열을 재현했다.
- **Unsteered와 Steer ctx는 재현됐다(±1.3%p 이내).**
- **Steer par는 부분적으로만 재현됐다.** 공개 코드의 α 선택 기준을 그대로 쓰면 -20.7%p, 논문 지표 기준으로 α를 고르면 -9.2%p다.
- 논문 Table 1 수치는 논문 Appendix C의 채점 방식이 아니라 **공개 코드의 채점 방식(첫 문장, both도 정답 처리)과 일치한다.**

## 2. 실험 설정

| 항목 | 값 |
|---|---|
| 모델 | Llama-3.1-8B-Instruct (bf16, eager attention, greedy, max_new_tokens=200) |
| 데이터 | `pminervini/NQ-Swap` dev 4,746행 |
| cohort | 문맥 없이 맞힌 행(stage1_correct) **2,331행** → train 1,632 / val 350 / test 349 (seed 42) |
| 개입 | layer 10 residual 출력에 α·v 추가 (v = mean(clean) − mean(conflict), train 행으로 계산) |
| α 탐색 | α⁺: 0 ~ 3.0, α⁻: −3.0 ~ −0.2 (간격 0.2, val에서 선택) |
| 환경 | Colab NVIDIA A100-SXM4-80GB · transformers 4.46.3 · torch 2.14.1+cu130 · tokenizers 0.20.3 · accelerate 1.15.0 |
| batch | 16 (64는 stage2에서 35.33 GiB 할당 OOM, 40 GB GPU에서는 32도 OOM) |

## 3. 결과 (test 349행)

### 3-1. Table 1 비교 (upstream 채점: 첫 문장 기준)

| 설정 | α | Acc_par | Acc_ctx | 논문 | 판정 |
|---|---|---|---|---|---|
| Unsteered | 0 | 32.4 | 48.7 | 33.7 / 49.4 | ✅ 재현 |
| Steer ctx | −0.8 | – | **54.2** | 55.5 | ✅ 재현 (−1.3%p) |
| Steer par (upstream 기준 선택) | 2.4 | **36.1** | – | 56.8 | ❌ −20.7%p |
| Steer par (Acc_par/N 기준 선택) | 1.6 | **47.6** | – | 56.8 | △ −9.2%p |

- upstream은 α⁺를 `correct / stage2_runs`(stage2를 실행한 행 중 정답 비율)로 고른다. 논문의 Acc_par는 `correct / N`(전체 test 행 기준)이다. 기준이 달라 α⁺가 2.4로 과하게 선택됐다.
- α⁻는 upstream에 선택 기능이 없어, 재현 스크립트(`scripts/table1.py`)가 val `wrong / N` 최대값으로 선택했다.

### 3-2. 논문 방식 재채점 (전체 출력, 4가지 라벨)

| 설정 | par-only | ctx-only | both | neither |
|---|---|---|---|---|
| Unsteered (α=0) | 17.2 | 28.7 | **47.6** | 6.6 |
| Steer par (α=2.4) | 36.1 | 2.9 | 2.6 | **58.5** |
| Steer par (α=1.6) | 49.6 | 6.9 | 4.6 | 39.0 |
| Steer ctx (α=−0.8) | 9.7 | 47.3 | 23.2 | 19.8 |

- Unsteered에서 **두 답을 함께 말한 경우(both)가 47.6%**다. upstream 채점은 첫 문장만 보고 both도 정답으로 세기 때문에 수치가 높게 나온다.
- α=2.4에서는 **neither가 58.5%**다. 이 중 51.0%p는 steering된 상태로 문맥 없는 질문을 다시 풀다 틀려 stage2를 실행하지 않은 행(`not_run`)이고, 실제로 두 답 모두 말하지 않은 출력은 7.4%다.
- 단어 경계(`\b`) 일치로 다시 채점해도 라벨별 차이는 0.6%p 이내였다(최대: α=2.4의 par-only 36.1 → 36.7). 짧은 답(정규화 후 3자 이하) 행은 18개다.

## 4. 주요 발견

1. **논문 Table 1은 공개 코드 채점과 일치한다.** Unsteered를 논문 방식으로 채점하면 17.2 / 28.7로 논문(33.7 / 49.4)과 크게 다르다. 첫 문장 채점으로는 32.4 / 48.7로 일치한다. 논문 Appendix C의 채점 설명(256토큰, par-only만 정답)과 실제 수치가 맞지 않는다.
2. **par 재현 차이는 채점이 아니라 steering 절차에서 생긴다.**
   - α 선택 기준 차이가 가장 큰 요인이다(−20.7%p → −9.2%p).
   - 공개 코드는 문맥 없는 질문을 다시 풀 때도 개입한다. 그래서 |α|가 커지면 원래 맞히던 질문도 틀리고, 이 행은 0점으로 분모에 남는다. α=1.6에서 test 106행, α=−3.0에서 val 306행이 이 단계에서 탈락했다.
   - 논문 본문은 "conflict 프롬프트의 마지막 토큰에만 개입"한다고 썼지만, 코드는 모든 위치와 모든 생성 step에 개입한다.
3. **논문 설정의 batch 64는 공개 코드로 실행할 수 없었다.** A100 80GB에서도 긴 문맥(약 2,150토큰) batch에서 OOM이 나 batch 16으로 낮췄다.

## 5. SOTA 비교 시 사용 방침 (제안)

- **주 비교값: α⁺=1.6 결과(논문 지표 기준 선택)**와 α⁻=−0.8 결과를 쓴다.
- α⁺=2.4 결과는 "공개 코드 그대로 실행"으로 부록에 둔다.
- 채점은 팀 기준(strict EM)과 포함 여부를 함께 보고한다. 행별 출력(`stage2_output_raw`)이 저장되어 있어 GPU 재실행 없이 재채점할 수 있다.

## 6. 다음 단계

- [x] 결과 파일과 README 커밋: `SOTA/lou/steer_result/`, `SOTA/lou/results/logs/` (`sota/lou` 브랜치)
- [ ] 같은 출력을 strict EM으로 재채점
- [ ] 우리 방법(PO3)을 같은 split(seed 42)으로 NQ-Swap에서 실행해 비교
- [ ] Lou를 p8s에 적용 (데이터 형식 변환, K±/C± 4-state별 집계, C+ 손실 측정)
- [ ] Lou가 사용한 나머지 모델 3종과 ConFiQA로 확장

## 부록: 산출물 위치

| 항목 | 위치 |
|---|---|
| 실행 노트북 | `SOTA/lou/colab_run.ipynb` (`sota/lou` 브랜치) |
| 요약 (α⁺=2.4 기준) | `SOTA/lou/steer_result/table1_summary.json` (Drive `sota_lou/steer_result/`) |
| 요약 (α⁺=1.6 기준) | `SOTA/lou/steer_result/par_a1.6/table1_summary.json`. α=1.6 수치는 `paper_metric.runs.steer_par`에 있음 |
| 행별 test 출력 | `SOTA/lou/steer_result/{par,par_a1.6,ctx,base}/.../L10_alpha*_steer_result.json` |
| 실행 로그 | summary 로그: `SOTA/lou/results/logs/`. 전체 로그: Drive `sota_lou/logs/` |
| 실행 시간 | dump 약 2시간, α⁺ 탐색 약 2시간, α⁻ 탐색 약 2시간 (A100 80GB, batch 16) |
