# Contributing

This repository accepts contributions that strengthen the phone-first local application factory.

## Required proof

python3 -m py_compile $(find ai_workflow_os -name "*.py" -type f)
PYTHONPATH="$PWD" python3 -m pytest -q
bash scripts/verify_workflow_app.sh

## Good contributions

- Improve Termux ARM64 local execution
- Improve cross-device packaging
- Improve PWA installability
- Improve prompt bridge and approval flow
- Improve self-build executor safety
- Improve generated app quality
- Improve proof, audit, snapshots, and public repo hygiene
- Prepare future desktop, cloud, SaaS, and marketplace modes
