#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli serve --host 127.0.0.1 --port 8765
