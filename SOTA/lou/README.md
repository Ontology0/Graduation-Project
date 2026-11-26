# Lou et al. (arXiv 2610.20067) 재현: NQ-Swap · Llama-3.1-8B-Instruct

> **상태:** 실행 스크립트만 작성했고 아직 실행하지 않았습니다. 이 디렉터리에는 재현 결과가 없습니다.

목표는 논문 Table 1의 NQ-Swap Llama 열입니다.

| 설정 | Acc_par | Acc_ctx |
|---|---:|---:|
| Unsteered | 33.7 | 49.4 |
| Ours (layer 10, resid-post) | 56.8 | 55.5 |

`upstream/`은 원 저자 저장소([AheadOFpotato/knowledge_selection_steering](https://github.com/AheadOFpotato/knowledge_selection_steering))의 submodule이며 **수정하지 않습니다**. 이 디렉터리의 스크립트는 upstream 코드를 호출하기만 합니다. 예외는 `scripts/table1.py`의 α⁻ 선택 로직으로, upstream에 해당 기능이 없어 따로 작성했습니다([차이 7](#논문과-upstream-코드의-차이)).

## 파일

| 파일 | 역할 |
|---|---|
| [colab_run.ipynb](colab_run.ipynb) | Colab(L4/A100) 진입점: Drive 연결, `sota/lou` clone(`--recurse-submodules`), 설치, `HF_TOKEN` secret, 경로 설정, 단계별 실행 |
| [scripts/download_model.sh](scripts/download_model.sh) | `meta-llama/Llama-3.1-8B-Instruct` → `$MODEL_ROOT/Meta-Llama-3.1-8B-Instruct`(safetensors·json만, commit SHA를 `.hf_revision`에 기록) |
| [scripts/prepare_nqswap.sh](scripts/prepare_nqswap.sh) | `pminervini/NQ-Swap`(split `dev`, 4,746행) → `$DATA_ROOT/NQ-Swap/dev.jsonl`(행 변형 없음, revision·sha256을 `dev.meta.json`에 기록) |
| [scripts/run_nqswap_llama.sh](scripts/run_nqswap_llama.sh) | dump → 방향 추정 + α⁺ 탐색 + test → α⁻ 탐색 + test → unsteered test → 요약 |
| [scripts/table1.py](scripts/table1.py) | val grid에서 α⁻ 선택, test 결과로 Acc_par/Acc_ctx 계산(모델 실행 없음) |
| [scripts/rescore_paper_metric.py](scripts/rescore_paper_metric.py) | 같은 test 출력을 논문 Appendix C 방식으로 재채점(par-only/ctx-only/both/neither). α는 바꾸지 않음 |

## 실행

Colab에서 `colab_run.ipynb`를 위에서부터 실행합니다. 준비물은 다음과 같습니다.

- Colab Secrets의 `HF_TOKEN`: Llama 3.1 라이선스를 승인받은 계정이어야 하며, 노트북 접근을 허용해야 합니다.
- Drive 여유 공간 약 20 GB: 모델 약 16 GB에 dump가 더해집니다. dump NPZ는 행마다 32 layer × 4096 × fp16 × 2 prompt이며, 압축 전 기준 행당 약 0.5 MB입니다.

Drive 경로는 다음과 같습니다.

```text
/content/drive/MyDrive/sota_lou/
├── models/Meta-Llama-3.1-8B-Instruct/   MODEL_ROOT
├── data/NQ-Swap/dev.jsonl               DATA_ROOT
├── dump/llama3-8b-it/NQ-Swap/dev/       DUMP_ROOT
├── steer_result/{par,ctx_sweep,ctx,base}/llama3-8b-it/NQ-Swap/dev__dir_dev__test_dev/
│   └── table1_summary.json              STEER_OUT_ROOT
└── logs/
```

로컬 GPU 서버에서는 네 경로 변수와 `HF_TOKEN`을 export한 뒤 세 스크립트를 순서대로 실행하면 됩니다. upstream 셸 스크립트가 `${var,,}`를 쓰므로 bash 4 이상이 필요합니다.

## upstream에서 확인한 내용

모든 경로는 `upstream/` 기준입니다.

### 경로와 모델 키

- [src/project_paths.py](upstream/src/project_paths.py)는 `DATA_ROOT`, `DUMP_ROOT`, `MODEL_ROOT`, `STEER_OUT_ROOT`를 환경 변수로 받습니다. 기본값은 `data/`, `output/dump`, `models/`, `output/steer_result`입니다. [run/common.sh](upstream/run/common.sh)도 같은 변수를 존중합니다.
- `resolve_model_path`는 `llama3-8b-it`와 `llama3.1-8b-it`를 **둘 다** `$MODEL_ROOT/Meta-Llama-3.1-8B-Instruct`로 매핑합니다. 등록되지 않은 키는 HF hub id로 그대로 넘깁니다.
- **함정:** [run/run_dump_all_datasets.sh](upstream/run/run_dump_all_datasets.sh)는 `MODEL`이 아니라 `MODELS`를 읽고, 기본값은 `llama3-8b-it`입니다. 따라서 upstream README 예시처럼 `MODEL=llama3.1-8b-it`로 dump하면 `dump/llama3-8b-it/`에 저장됩니다. 반면 steering은 `MODEL=llama3.1-8b-it`이면 `dump/llama3.1-8b-it/`을 찾기 때문에 파일을 찾지 못합니다. 이 스크립트는 두 단계 모두 `MODEL_KEY=llama3-8b-it`를 씁니다. 그림 스크립트의 기본 키도 이 값입니다.

### 데이터

- NQ-Swap 입력은 `$DATA_ROOT/NQ-Swap/dev.jsonl` 하나로 고정되어 있습니다. dump 스크립트는 다른 파일명을 거부하고, category도 항상 `dev`로 둡니다.
- 행 형식은 `question`, `org_context`, `org_answer`(list), `sub_context`, `sub_answer`(list)입니다. upstream은 `org_context`와 `sub_context` 키가 있으면 `nq_swap`으로 인식합니다. `pminervini/NQ-Swap`의 열이 정확히 이 다섯 개라서 그대로 저장합니다. `<P>` 태그도 남깁니다.

### 1단계 dump: [src/dump_activations_from_testjsonl.py](upstream/src/dump_activations_from_testjsonl.py)

- 프롬프트에는 chat template을 적용하지 않습니다.
  - clean: `Question: {q}\nAnswer:`
  - 문맥 포함: `{context}\n\nQuestion: {q}\nAnswer:`
- 생성 설정: bf16, `attn_implementation="eager"`, left padding, `pad_token=eos`, greedy, `max_new_tokens=200`
- 채점은 생성문을 첫 문장 부호(`.!?`)까지 자른 뒤 소문자·공백 정규화한 substring 포함 여부로 합니다. 길이 2 미만의 정답 문자열은 무시합니다.
- 행 분류:
  - stage1 clean 답이 `org_answer`를 포함하면 `stage1_correct_use_wrong_context`입니다. stage2는 `sub_context`로 실행합니다.
  - 포함하지 않으면 `stage1_wrong_use_correct_context`입니다. stage2는 `org_context`로 실행합니다.
- stage2 label:
  - `org_answer`를 포함하면 `correct`
  - 그렇지 않고 `sub_answer`를 포함하면 `wrong`
  - 둘 다 없으면 `skipped`
- 출력: `$DUMP_ROOT/<model>/NQ-Swap/dev/`
  - `internal_aware_data__<group>.json`: manifest. 프롬프트·정답·label을 담습니다.
  - `resid_hidden_state__<group>.npz`: `resid_act_clean`, `resid_act_stage2`. 프롬프트 마지막 토큰의 모든 layer 출력(`hidden_states[1:]`)이며 fp16입니다.
- upstream 셸 스크립트는 `set -e` 없이 실행되어 python이 실패해도 0으로 끝납니다. `run_nqswap_llama.sh`는 dump 후 NPZ·manifest가 있는지 직접 확인합니다.

### 2단계 steering: [src/run_resid_projection_ablation.py](upstream/src/run_resid_projection_ablation.py)

[run/run_resid_projection_ablation.sh](upstream/run/run_resid_projection_ablation.sh)가 넘기는 인자는 다음과 같습니다.

```text
--eval-mode train_val_test --split-protocol same_dataset --split-seed 42
--train-ratio 0.7 --val-ratio 0.15 --model <key> --npz <dump>/resid_hidden_state__stage1_correct_use_wrong_context.npz
--test-json <dump>/internal_aware_data__stage1_correct_use_wrong_context.json --out-root $STEER_OUT_ROOT
--output-category dev --direction-category-tag dev --test-category-tag dev --gpu 0 --layers 10
--alpha-start 0 --alpha-end 3 --alpha-step 0.2 --batch-size 64
--max-samples-stage1 0 --max-samples-stage2 0 --stage1-min-pass-rate -1
```

- 실행 시점에 manifest 행을 seed 42로 섞어 70/15/15 split을 만듭니다([src/data_split.py](upstream/src/data_split.py)). 방향은 train 행만으로 `v = mean(resid_act_clean[L]) − mean(resid_act_stage2[L])`로 계산합니다.
- Hook은 `model.model.layers[L]`의 출력(resid-post)에 `α·v`를 더합니다. **모든 위치와 모든 생성 step**에 적용되며, stage1 clean 프롬프트 재실행에도 적용됩니다.
- 평가: 각 α에서 stage1(clean)을 다시 실행해 여전히 맞는 행만 stage2(`sub_context`)를 생성합니다. stage1에서 탈락한 행은 `not_run`이 됩니다.
- α 선택: val에서 `stage2_correct / stage2_runs`가 최대인 α를 고르고, 동점이면 |α|가 작은 쪽을 고릅니다. 이 α 하나로 test를 평가합니다.
- 출력: `<out-root>/<model>/NQ-Swap/dev__dir_dev__test_dev/`
  - `L10_val_alpha_grid.json`
  - `L10_alpha<α>_steer_result.json`(test, 행별 출력·label 포함)
- 기본 grid는 단일 실행 스크립트가 0..3, 일괄 스크립트(`run_resid_projection_ablation_all_final.sh`)가 0.2..3이며, 둘 다 step 0.2입니다.

### 지표

[src/plot_nqswap_alpha_curves_multi_model.py](upstream/src/plot_nqswap_alpha_curves_multi_model.py)는 `correct/N`을 internal(parametric), `wrong/N`을 external(contextual)로 계산합니다. `N`은 manifest 전체 행 수이므로 `skipped`·`not_run`도 분모에 들어갑니다. 논문 Table 13도 batch 64(NQ-Swap), bf16, eager, greedy, `max_new_tokens=200`, A100 80GB를 명시합니다.

## 이 스크립트의 실행 순서

| 단계 | 호출 | 출력(`$STEER_OUT_ROOT/…`) |
|---|---|---|
| `dump` | `run/run_dump_all_datasets.sh`(`MODELS=llama3-8b-it DATASETS=NQ-Swap`) | `$DUMP_ROOT/…` |
| `par` | `run/run_resid_projection_ablation.sh`, α 0..3 | `par/`: val-selected α⁺의 test → **Acc_par** |
| `ctx` | 같은 python, α −3..−0.2 val sweep → `table1.py`가 val `wrong/N` 최대 α⁻ 선택 → α⁻ 단일 실행 | `ctx_sweep/`, `ctx/` → **Acc_ctx** |
| `base` | 같은 python, α=0 | `base/` → Unsteered |
| `summary` | `table1.py summarize` → `rescore_paper_metric.py` | `table1_summary.json`(upstream 방식 + `paper_metric`) |

### 두 가지 채점 방식

`summary` 단계는 같은 test 출력(base, α⁺, α⁻)에 대해 두 방식의 수치를 나란히 출력합니다. `rescore_paper_metric.py`는 `table1.py`가 고른 test 파일을 그대로 쓰며, α를 다시 고르지 않습니다.

| | upstream 방식(`table1.py`) | 논문 방식(`rescore_paper_metric.py`) |
|---|---|---|
| 판정 범위 | `stage2_output_raw`의 첫 문장 | `stage2_output_raw` 전체(최대 200 토큰) |
| 정규화 | 소문자, 공백 정리 | Appendix C.1: 소문자, intra-token hyphen 외 구두점 제거, 앞 관사(a/an/the) 제거, 공백 정리 |
| 정답 문자열 | 길이 2 미만 제외 | 빈 문자열만 제외. `org_answer`·`sub_answer`의 모든 alias |
| Acc_par | `correct`/N(`sub_answer`가 함께 있어도 포함) | par-only/N |
| Acc_ctx | `wrong`/N | ctx-only/N |
| `not_run` | 분모에만 포함 | neither |

N은 두 방식 모두 test 전체 행 수입니다. upstream의 행별 test 출력에는 첫 `sub_answer`(`distracted_token`)만 남아 있어서, 전체 alias 목록은 dump manifest에서 `line_idx`로 가져옵니다. 결과는 `table1_summary.json`의 `paper_metric.runs.{unsteered,steer_par,steer_ctx}`에 저장되며, 각 항목에 upstream 수치·논문 수치·4가지 라벨 개수와 비율이 들어갑니다.

보조 진단(`aux`)은 보고 지표가 아닙니다. 짧은 답이 우연히 substring으로 일치하는 정도를 가늠하는 용도이며, 두 가지를 기록합니다.

- 정규화 후 길이 3자 이하인 alias를 가진 행 수(`rows_with_short_answer`: any·par·ctx)
- 같은 정규화 텍스트를 단어 경계(`\b`) 일치로 판정한 4가지 라벨 분포(`word_boundary`)

예를 들어 "23"은 "1723"에 substring으로 포함되지만, 단어 경계 기준으로는 일치하지 않습니다.

세 steering 실행은 같은 seed로 같은 split을 만들기 때문에 방향 벡터와 val/test 행이 모두 같습니다. 각 단계는 완료된 결과가 있으면 건너뛰고, `FORCE=1`로 다시 계산합니다.

`ctx_sweep`과 `ctx` 실행에서 upstream은 구조상 test 평가를 한 번 더 합니다. 각각 `correct/runs` 기준 α와 단일 α에 대한 val 평가이며, Table 1에는 쓰지 않습니다.

## 논문과 upstream 코드의 차이

재현 결과를 해석할 때 고려해야 할 차이입니다. 이 스크립트는 upstream 동작을 따르고, 차이를 보정하지 않습니다.

1. **평가 cohort:** 논문 §3은 clean 질문과 paraphrase 4개를 모두 맞히고 conflict에서 주입된 답을 낸 항목만 남긴다고 씁니다. 코드에는 paraphrase나 conflict 응답 기준 필터가 없고 clean 정답 여부만 봅니다. 논문 Appendix D가 base cohort를 `stage1_correct_use_wrong_context`로 부르는 점은 코드와 일치합니다.
2. **데이터 필터:** 논문은 "question-deduplicated split without tables or list items"라고 씁니다. upstream에는 이 필터가 없어 `pminervini/NQ-Swap` 4,746행을 그대로 씁니다. 저자가 별도로 필터링한 파일을 썼는지는 확인할 수 없습니다.
3. **개입 위치:** 논문은 conflict 프롬프트 마지막 토큰에만 더한다고 씁니다. 코드는 layer 출력의 모든 위치와 생성 step에 더하고, stage1 clean 재실행에도 적용합니다.
4. **채점 범위:** 논문은 처음 256 토큰을 보고 parametric-only를 Acc_par로 셉니다. 코드는 첫 문장만 보고, `org_answer`가 있으면 `sub_answer`가 함께 있어도 `correct`로 셉니다. `rescore_paper_metric.py`가 논문 방식 수치를 따로 계산합니다([두 가지 채점 방식](#두-가지-채점-방식)).
5. **생성 길이:** upstream은 `max_new_tokens=200`으로 생성합니다(논문 Table 13도 200). 반면 논문 Appendix C.2의 판정 창은 256 토큰입니다. 생성이 200 토큰에서 끝나므로 논문 방식 재채점도 최대 200 토큰만 봅니다. 201–256번째 토큰에만 답이 나오는 행은 neither가 되어, 논문 수치보다 낮게 나올 수 있습니다. 256 토큰으로 맞추려면 upstream 상수를 바꿔 다시 생성해야 하는데, upstream을 수정하지 않는 원칙에 따라 그렇게 하지 않습니다.
6. **α⁺ 선택 지표:** upstream은 val `correct/stage2_runs`, Table 1의 Acc_par는 `correct/N`입니다. upstream을 그대로 쓰되, `/N` 기준이었다면 고를 α를 요약에 함께 기록합니다(`alpha_plus_if_selected_by_val_acc_par`).
7. **α⁻ 선택:** 논문 Appendix B는 (α⁺, α⁻)를 val에서 각각 고른다고 씁니다. upstream `train_val_test`는 `correct` 기준 선택만 있어 음수 grid에서는 α⁻를 고를 수 없습니다. 그래서 `scripts/table1.py`가 val `wrong/N`(Acc_ctx 정의) 최대값으로 고릅니다. 이 부분은 **이 저장소의 선택**이며 원 코드에 없습니다.
8. **Batch 크기:** 논문은 64(A100 80GB)입니다. 노트북은 GPU 메모리에 따라 64(≥70 GB), 32(≥35 GB, A100 40GB), 8(L4)을 고릅니다. left padding과 bf16 때문에 batch 구성이 greedy 출력을 미세하게 바꿀 수 있습니다.
9. **Layer:** 논문은 clean/conflict cosine 최소 layer를 고르고, Llama 기본값은 10입니다. 여기서는 요청 조건대로 10으로 고정합니다.
10. **미기재 환경:** 논문에는 모델 revision과 transformers 버전이 없습니다. 노트북은 `transformers==4.46.3`으로 고정하고, 모델과 데이터 commit SHA를 파일로 남깁니다.

## 결과

아직 실행하지 않았습니다. 실행 후에는 `table1_summary.json`의 값과 함께 다음 정보를 기록합니다.

- GPU 종류
- batch 크기
- transformers 버전
- 모델·데이터 SHA
- dump cohort 크기
- 선택된 α⁺와 α⁻
