#!/usr/bin/env bash
# Write NQ-Swap to  $DATA_ROOT/NQ-Swap/dev.jsonl  (the only file upstream reads).
#
# upstream/run/run_dump_all_datasets.sh hard-codes NQ_SWAP_JSONL=$DATA_ROOT/NQ-Swap/dev.jsonl,
# and dump_activations_from_testjsonl.py refuses any other file name for NQ-Swap.
# Row schema it detects as "nq_swap": question, org_context, org_answer, sub_context,
# sub_answer. pminervini/NQ-Swap (split "dev", 4746 rows) has exactly these columns,
# so rows are written unchanged (no <P> stripping, no dedup, no filtering).
#
# Required env:  DATA_ROOT
# Optional env:  NQSWAP_REPO (default pminervini/NQ-Swap), NQSWAP_REVISION (default main),
#                HF_ENDPOINT (default https://huggingface.co), FORCE=1 to rewrite.
set -euo pipefail

: "${DATA_ROOT:?set DATA_ROOT}"
export HF_ENDPOINT="${HF_ENDPOINT:-https://huggingface.co}"
NQSWAP_REPO="${NQSWAP_REPO:-pminervini/NQ-Swap}"
NQSWAP_REVISION="${NQSWAP_REVISION:-main}"
OUT="${DATA_ROOT}/NQ-Swap/dev.jsonl"
FORCE="${FORCE:-0}"

mkdir -p "$(dirname "${OUT}")"
if [[ -s "${OUT}" && "${FORCE}" != "1" ]]; then
  echo "[prepare_nqswap] exists ($(wc -l < "${OUT}") rows): ${OUT}  (FORCE=1 to rewrite)"
  exit 0
fi

python3 - "${NQSWAP_REPO}" "${NQSWAP_REVISION}" "${OUT}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

from datasets import load_dataset
from huggingface_hub import HfApi

repo, revision, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
sha = HfApi().dataset_info(repo, revision=revision).sha
ds = load_dataset(repo, split="dev", revision=sha)

required = ["question", "org_context", "org_answer", "sub_context", "sub_answer"]
missing = [c for c in required if c not in ds.column_names]
if missing:
    sys.exit(f"[prepare_nqswap] missing columns {missing}; got {ds.column_names}")

tmp = out.with_suffix(".jsonl.tmp")
with tmp.open("w", encoding="utf-8") as f:
    for row in ds:
        f.write(json.dumps({c: row[c] for c in required}, ensure_ascii=False) + "\n")
tmp.replace(out)

digest = hashlib.sha256(out.read_bytes()).hexdigest()
meta = {"repo": repo, "revision": sha, "split": "dev", "num_rows": len(ds), "sha256": digest}
# Sibling file; upstream only reads dev.jsonl.
out.with_name("dev.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
print(f"[prepare_nqswap] wrote {len(ds)} rows -> {out}")
print(json.dumps(meta))
PY
