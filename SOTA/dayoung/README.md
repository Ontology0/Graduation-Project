# sota_bench — 기준선 ①② 재현 + SOTA 비교 하네스

> **업로드 상태 안내 (2026-10-27):** 아래는 의도한 실행 구조입니다. 현재 파일은 flat하게 업로드되어 있고 `common/`·`methods/` 패키지가 없어 그대로 실행할 수 없습니다. 실제 파일 위치·미구현 방법·외부 입력은 [SOTA 안내](../README.md)를 먼저 확인하세요.

p8s-v2(612질문 × C± = 1,224행)에서 우리 기준선과 팀원별 SOTA 논문을
같은 프롬프트·같은 채점으로 붙이기 위한 코드다.

## 설계 원칙 — 재구현하지 않는다

기준선 ①②는 **A0/A1 노트북이 이미 검증을 통과한 산출물을 조회**한다.
A0-4에서 현경 `exp2_P9_r0.06.parquet` 대비 문자열 불일치 ≤20/1224로 확인된 것이므로,
다시 구현하면 그 검증을 처음부터 다시 통과해야 한다. 그럴 이유가 없다.

| 기준선 | 출처 | GPU |
|---|---|---|
| `base` | `A0_headroom/gen_base.parquet` | 불필요 |
| `always_retain` (②) | `gen_late_ret_r0.06.parquet` — P9 · ρ0.06 · L14–18 · w_v3 | 불필요 |
| `late_router` (①) | A1 정책 로직 + `gen_*.parquet` 조회 | 불필요 |
| SOTA | 새로 생성 | **필요** |

①이 GPU 없이 되는 이유: 한 행에 early/late 중 하나만 개입하므로 greedy에서는
결과표 조회가 실제 생성과 같다. A1도 같은 이유로 GPU를 쓰지 않는다.

## 경로

```bash
export ABENCH_ROOT="/content/drive/MyDrive/11주차_A축_실험(ldy)/"
# 필요하면 개별 지정
export ABENCH_P9="$ABENCH_ROOT/P9/"       # 현경 공유 폴더 (읽기 전용)
export ABENCH_A0="$ABENCH_ROOT/A0_headroom/"
```

**먼저 확인할 것**: `P9/` 바로가기 접근이 살아 있는지. 끊겼으면 여기서 멈춘다.
`w_v3.npz`·`p8s_prompt.py`·`labels_v3`·`cb_v3`·`row_manifest`가 전부 그 안에 있다.

## 실행

```bash
pip install -q pandas pyarrow scikit-learn scipy numpy

# 기준선 — CPU, 수 분
python run.py --method base
python run.py --method always_retain      # 재현 확인: EM 0.5997
python run.py --method late_router        # 재현 확인: EM 0.6078
python run.py --method always_retain_r09  # C+ 비열등 실패 대조군

# SOTA — GPU
python run.py --method cad
python run.py --method adacad
python run.py --method spare              # 구현 후

python compare.py --ref base --out table.md
```

`run.py`가 보고값과 대조해 `[재현 확인] ... OK / 불일치`를 출력한다.
불일치가 뜨면 SOTA로 넘어가지 않는다 — 경로나 산출물 버전 문제다.

## 채점 방향 — 표 각주에 반드시 넣을 것

**C+/C− 양쪽 모두 "사실"을 gold로 채점한다.**

| 계열 | gold | 예 |
|---|---|---|
| context-faithful | 변조된 문맥의 답 | CAD, AdaCAD, COIECD, CoCoA |
| conflict-resolution (우리) | 사실 | SpARE, SHIFT, Knowledgeable-R1 |

CAD 계열은 우리 채점에서 C−가 base보다 **낮게 나오는 것이 정상**이다. 이기려고
넣는 게 아니라 **과제 설정이 다르다는 증거**로 싣는다. `compare.py`가 각주를 자동으로 단다.

## 팀원 배정

| 순위 | 논문 | 위치 |
|---|---|---|
| 1 | **SpARE** (NAACL 2025) | `methods/sota_stubs.py::SpARE` |
| 2 | SHIFT (2026) | `methods/sota_stubs.py::SHIFT` |
| 3 | COIECD · CoCoA | `methods/sota_stubs.py` |
| — | CAD · AdaCAD | `methods/sota_contrastive.py` — **구현 완료** |

구현 규칙: **`common/` 은 건드리지 않는다.** `methods/`에 클래스 하나만 추가하고,
생성은 `common.generate.Runner`, 채점은 `common.scoring.make_scorer`만 쓴다.

**SpARE 담당자가 착수 전 확인할 것**: Llama-3.1-8B용 사전학습 SAE가 있는지.
없어서 백본을 Llama-3-8B로 바꿔야 하면 A0/A1 기준선을 전부 다시 측정해야 한다.

## A0와 반드시 같아야 하는 것

SOTA 생성에서 하나라도 어긋나면 기준선과 비교할 수 없다. `common/generate.py`가
전부 강제하지만, 수정할 일이 생기면 이 목록을 확인한다.

- `transformers==5.17.0`, model revision 고정(`manifest_cell1.json`), deterministic, tf32 off
- `PP.build_messages` + `apply_chat_template`, 행별 `prompt_md5` 검증
- `padding_side='left'`, BS=16, `n_prompt_tok` 정렬
- EOS에 `<|eot_id|>` 포함, `max_new_tokens = PP.MAX_NEW_TOKENS`
- 채점은 `trunc_v3` + `PP.norm` (SQuAD 표준 정규화를 쓰면 보고값과 어긋난다)
- steering: prefill은 attention mask로 비패딩 토큰 전체(P9), decode는 마지막 위치

## 알려진 한계 (보고서에 그대로 싣는다)

- p8s 단일 개발셋이다. 동결 설정·w·강도가 전부 p8s에서 결정됐다
- `late_router`의 +0.82%p는 약 10행 차이다. 1,224행 규모에서 유의 판정이 어렵다
- 외부 데이터(NQ-Swap, ConFiQA)는 아직 연결돼 있지 않다 — baseline 부재와 같은 급으로 시급한 공백
- base가 A0 0.5310 / E16-2(packed) 0.530으로 갈려 있다. bf16 배치 민감도로 설명되는 차이지만,
  ①②③를 한 표에 올릴 때는 paired bootstrap의 pairing이 깨지므로 base를 재측정해 통일한다.
  비교표를 조판하기 직전에 처리하면 된다 (생성 1회, 10~15분)
