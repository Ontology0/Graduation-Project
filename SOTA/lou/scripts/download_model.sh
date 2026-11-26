#!/usr/bin/env bash
# Download Llama-3.1-8B-Instruct into the folder name upstream expects.
#
# upstream/src/project_paths.py maps both model keys "llama3-8b-it" and
# "llama3.1-8b-it" to  $MODEL_ROOT/Meta-Llama-3.1-8B-Instruct  (local path, not a
# hub id), so the weights must live exactly there.
#
# Required env:  MODEL_ROOT, HF_TOKEN (account with Llama 3.1 license accepted)
# Optional env:  HF_REPO (default meta-llama/Llama-3.1-8B-Instruct)
#                HF_REVISION (default main; the resolved commit is recorded)
#                HF_ENDPOINT (default https://huggingface.co)
#
# Usage:  MODEL_ROOT=/content/drive/MyDrive/sota_lou/models bash download_model.sh
set -euo pipefail

: "${MODEL_ROOT:?set MODEL_ROOT}"
: "${HF_TOKEN:?set HF_TOKEN (Colab: Secrets -> HF_TOKEN)}"
export HF_ENDPOINT="${HF_ENDPOINT:-https://huggingface.co}"
HF_REPO="${HF_REPO:-meta-llama/Llama-3.1-8B-Instruct}"
HF_REVISION="${HF_REVISION:-main}"
DEST="${MODEL_ROOT}/Meta-Llama-3.1-8B-Instruct"

mkdir -p "${DEST}"
echo "[download_model] ${HF_REPO}@${HF_REVISION} -> ${DEST} (endpoint ${HF_ENDPOINT})"

python3 - "${HF_REPO}" "${HF_REVISION}" "${DEST}" <<'PY'
import json
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

repo, revision, dest = sys.argv[1], sys.argv[2], Path(sys.argv[3])
token = os.environ["HF_TOKEN"]


def complete(d: Path) -> bool:
    idx = d / "model.safetensors.index.json"
    needed = ["config.json", "tokenizer.json", "tokenizer_config.json"]
    if not idx.is_file() or not all((d / n).is_file() for n in needed):
        return False
    shards = set(json.loads(idx.read_text())["weight_map"].values())
    return all((d / s).is_file() and (d / s).stat().st_size > 0 for s in shards)


sha = HfApi().model_info(repo, revision=revision, token=token).sha
rev_file = dest / ".hf_revision"
if complete(dest) and rev_file.is_file() and rev_file.read_text().split()[-1] == sha:
    print(f"[download_model] already complete at {sha}; skip")
    sys.exit(0)

# Only HF-format weights + tokenizer/config. "original/" (Meta consolidated .pth,
# ~16 GB) is not used by transformers and is skipped.
snapshot_download(
    repo_id=repo,
    revision=sha,
    local_dir=str(dest),
    token=token,
    allow_patterns=["*.json", "*.safetensors"],
)
if not complete(dest):
    sys.exit(f"[download_model] incomplete download under {dest}")
rev_file.write_text(f"{repo} {sha}\n")
print(f"[download_model] done: {repo}@{sha}")
PY
