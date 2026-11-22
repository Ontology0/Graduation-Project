#!/usr/bin/env bash
# Lou et al. Table 1, NQ-Swap, Llama-3.1-8B-Instruct, layer 10.
# Calls upstream code unchanged; only orchestration lives here.
#
# Steps (STEPS, comma-separated; default all, in this order):
#   dump  upstream/run/run_dump_all_datasets.sh  (stage1 closed-book, stage2 with context,
#         last-token resid of every layer) -> $DUMP_ROOT/<model>/NQ-Swap/dev/
#   par   upstream/run/run_resid_projection_ablation.sh: direction v = mean(clean) -
#         mean(conflict) on the 70% train split, alpha grid 0..ALPHA_MAX on the 15% val
#         split, test (15%) at the val-selected alpha+       -> $STEER_OUT_ROOT/par/
#   ctx   same python entry point; val sweep -ALPHA_MAX..-ALPHA_STEP -> ctx_sweep/,
#         alpha- = argmax val N_wrong/N (scripts/table1.py), then test at alpha- -> ctx/
#   base  same python entry point at alpha=0 (unsteered test) -> base/
#   summary  scripts/table1.py summarize -> $STEER_OUT_ROOT/table1_summary.json, then
#         scripts/rescore_paper_metric.py adds paper-protocol (App. C) scores to that file
#
# Required env: MODEL_ROOT DATA_ROOT DUMP_ROOT STEER_OUT_ROOT
# Optional env: MODEL_KEY (llama3-8b-it) LAYER (10) GPU (0) BATCH_SIZE (64; paper value)
#               ALPHA_MAX (3) ALPHA_STEP (0.2) SPLIT_SEED (42) STEPS FORCE=1
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM="$(cd "${HERE}/../upstream" && pwd)"
PY="${UPSTREAM}/src/run_resid_projection_ablation.py"

: "${MODEL_ROOT:?}" "${DATA_ROOT:?}" "${DUMP_ROOT:?}" "${STEER_OUT_ROOT:?}"
export MODEL_ROOT DATA_ROOT DUMP_ROOT STEER_OUT_ROOT

# upstream/run/run_dump_all_datasets.sh reads MODELS (not MODEL; default llama3-8b-it), and
# the steering script reads dumps from $DUMP_ROOT/$MODEL. Use one key for both.
# llama3-8b-it and llama3.1-8b-it both resolve to Meta-Llama-3.1-8B-Instruct.
MODEL_KEY="${MODEL_KEY:-llama3-8b-it}"
LAYER="${LAYER:-10}"
GPU="${GPU:-0}"
BATCH_SIZE="${BATCH_SIZE:-64}"
ALPHA_MAX="${ALPHA_MAX:-3}"
ALPHA_STEP="${ALPHA_STEP:-0.2}"
SPLIT_SEED="${SPLIT_SEED:-42}"
STEPS="${STEPS:-dump,par,ctx,base,summary}"
FORCE="${FORCE:-0}"

GROUP="stage1_correct_use_wrong_context"
DUMP_DIR="${DUMP_ROOT}/${MODEL_KEY}/NQ-Swap/dev"
NPZ="${DUMP_DIR}/resid_hidden_state__${GROUP}.npz"
MANIFEST="${DUMP_DIR}/internal_aware_data__${GROUP}.json"
SLUG="dev__dir_dev__test_dev"

want() { [[ ",${STEPS}," == *",$1,"* ]]; }
log() { echo "[run_nqswap_llama $(date +%H:%M:%S)] $*" >&2; }
done_in() {  # done_in <out_root> <alpha>: test result exists for that alpha
  [[ "${FORCE}" != "1" && -f "$1/${MODEL_KEY}/NQ-Swap/${SLUG}/L${LAYER}_alpha$2_steer_result.json" ]]
}

# Same arguments as upstream/run/run_resid_projection_ablation.sh, minus the alpha grid.
steer() {  # steer <out_root> <alpha_start> <alpha_end> <alpha_step>
  python3 "${PY}" \
    --eval-mode train_val_test --split-protocol same_dataset \
    --split-seed "${SPLIT_SEED}" --train-ratio 0.7 --val-ratio 0.15 \
    --model "${MODEL_KEY}" --npz "${NPZ}" --test-json "${MANIFEST}" \
    --out-root "$1" --output-category dev \
    --direction-category-tag dev --test-category-tag dev \
    --gpu "${GPU}" --layers "${LAYER}" \
    --alpha-start "$2" --alpha-end "$3" --alpha-step "$4" \
    --batch-size "${BATCH_SIZE}" \
    --max-samples-stage1 0 --max-samples-stage2 0 --stage1-min-pass-rate -1
}

[[ -f "${MODEL_ROOT}/Meta-Llama-3.1-8B-Instruct/config.json" ]] \
  || { log "model missing: run scripts/download_model.sh"; exit 1; }
[[ -s "${DATA_ROOT}/NQ-Swap/dev.jsonl" ]] \
  || { log "data missing: run scripts/prepare_nqswap.sh"; exit 1; }
log "model=${MODEL_KEY} layer=${LAYER} batch=${BATCH_SIZE} alpha=±${ALPHA_MAX}/${ALPHA_STEP} steps=${STEPS}"
mkdir -p "${STEER_OUT_ROOT}"

if want dump; then
  log "1/4 dump -> ${DUMP_DIR}"
  # upstream script runs without `set -e` and exits 0 even if python fails: check outputs.
  MODELS="${MODEL_KEY}" DATASETS=NQ-Swap GPU="${GPU}" BATCH_SIZE="${BATCH_SIZE}" \
    SKIP_EXISTING=$([[ "${FORCE}" == "1" ]] && echo 0 || echo 1) \
    bash "${UPSTREAM}/run/run_dump_all_datasets.sh"
  for f in "${NPZ}" "${MANIFEST}"; do
    [[ -s "${f}" ]] || { log "dump output missing: ${f}"; exit 1; }
  done
  python3 -c 'import json,sys; o=json.load(open(sys.argv[1])); print("[dump]", o["group"], o["num_kept"], "rows")' "${MANIFEST}"
fi

if want par; then
  log "2/4 direction + alpha+ search (0..${ALPHA_MAX}) on val + test -> ${STEER_OUT_ROOT}/par"
  grid="${STEER_OUT_ROOT}/par/${MODEL_KEY}/NQ-Swap/${SLUG}/L${LAYER}_val_alpha_grid.json"
  if [[ "${FORCE}" != "1" && -f "${grid}" ]] && done_in "${STEER_OUT_ROOT}/par" \
      "$(python3 -c 'import json,sys; print(format(json.load(open(sys.argv[1]))["best_alpha"], "g"))' "${grid}")"; then
    log "par: results exist, skip"
  else
    MODEL="${MODEL_KEY}" DATASET=NQ-Swap CATEGORY=dev LAYERS="${LAYER}" GPU="${GPU}" \
      BATCH_SIZE="${BATCH_SIZE}" ALPHA_START=0 ALPHA_END="${ALPHA_MAX}" ALPHA_STEP="${ALPHA_STEP}" \
      SPLIT_SEED="${SPLIT_SEED}" STEER_OUT_ROOT="${STEER_OUT_ROOT}/par" \
      bash "${UPSTREAM}/run/run_resid_projection_ablation.sh"
  fi
fi

if want ctx; then
  log "3/4 alpha- search (-${ALPHA_MAX}..-${ALPHA_STEP}) on val -> ${STEER_OUT_ROOT}/ctx_sweep"
  sweep_grid="${STEER_OUT_ROOT}/ctx_sweep/${MODEL_KEY}/NQ-Swap/${SLUG}/L${LAYER}_val_alpha_grid.json"
  if [[ "${FORCE}" == "1" || ! -f "${sweep_grid}" ]]; then
    # Upstream also runs a test pass at the alpha maximising stage2_correct/runs; that
    # file is not used for Table 1.
    steer "${STEER_OUT_ROOT}/ctx_sweep" "-${ALPHA_MAX}" "-${ALPHA_STEP}" "${ALPHA_STEP}"
  fi
  a_minus="$(python3 "${HERE}/table1.py" select-ctx-alpha \
    --sweep-root "${STEER_OUT_ROOT}/ctx_sweep" --model "${MODEL_KEY}" --layer "${LAYER}" \
    --out "${STEER_OUT_ROOT}/ctx/selected_alpha.json")"
  log "alpha- = ${a_minus}; test -> ${STEER_OUT_ROOT}/ctx"
  if done_in "${STEER_OUT_ROOT}/ctx" "${a_minus}"; then
    log "ctx: results exist, skip"
  else
    steer "${STEER_OUT_ROOT}/ctx" "${a_minus}" "${a_minus}" "${ALPHA_STEP}"
  fi
fi

if want base; then
  log "4/4 unsteered test (alpha=0) -> ${STEER_OUT_ROOT}/base"
  if done_in "${STEER_OUT_ROOT}/base" 0; then
    log "base: results exist, skip"
  else
    steer "${STEER_OUT_ROOT}/base" 0 0 "${ALPHA_STEP}"
  fi
fi

if want summary; then
  python3 "${HERE}/table1.py" summarize \
    --steer-root "${STEER_OUT_ROOT}" --model "${MODEL_KEY}" --layer "${LAYER}"
  # Same test files, re-scored with the paper's Appendix C protocol (no alpha change).
  python3 "${HERE}/rescore_paper_metric.py" \
    --steer-root "${STEER_OUT_ROOT}" --manifest "${MANIFEST}"
fi
log "done"
