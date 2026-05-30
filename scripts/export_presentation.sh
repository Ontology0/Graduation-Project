#!/usr/bin/env bash
# Export docs/presentation.md → docs/presentation.pdf (Marp)
# --allow-local-files is required for <img src="assets/..."> in the deck.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

npx --yes @marp-team/marp-cli \
  docs/presentation.md \
  --pdf \
  --no-stdin \
  --allow-local-files \
  -o docs/presentation.pdf

echo "Wrote docs/presentation.pdf"
