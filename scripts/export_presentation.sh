#!/usr/bin/env bash
# Export docs/presentation.md → PDF + PPTX (Marp)
# --allow-local-files is required for <img src="assets/..."> in the deck.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMMON=(docs/presentation.md --no-stdin --allow-local-files)

npx --yes @marp-team/marp-cli "${COMMON[@]}" --pdf -o docs/presentation.pdf
npx --yes @marp-team/marp-cli "${COMMON[@]}" --pptx -o docs/presentation/presentation.pptx

echo "Wrote docs/presentation.pdf"
echo "Wrote docs/presentation/presentation.pptx"
