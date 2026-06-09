#!/usr/bin/env bash
set -euo pipefail
echo "=== AI Workflow OS Verify ==="
test -f README.md
test -f VERSION
test -f standards/OMEGA_ALPHA_STANDARD.md
test -f standards/CS101_ENGINEERING_STANDARD.md
test -f standards/AI_MODEL_SAFETY_STANDARD.md
test -f workflow/UNIVERSAL_APP_FACTORY.md
test -f workflow/UI_BACKEND_CONTRACT_STANDARD.md
test -f scripts/install_into_project.sh
echo "PASS: core workflow files exist."
