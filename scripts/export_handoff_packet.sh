#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-.}"
OUT="${2:-$HOME/storage/downloads}"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli export-packet "$TARGET" --out "$OUT"
