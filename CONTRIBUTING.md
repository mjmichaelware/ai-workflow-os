# Contributing

This repository accepts contributions that strengthen the phone-first local application factory.

## Required proof

python3 -m py_compile $(find ai_workflow_os -name "*.py" -type f)
PYTHONPATH="$PWD" python3 -m pytest -q
bash scripts/verify_workflow_app.sh

## Good contributions

- improve Termux ARM64 local execution
- improve cross-device packaging
- improve PWA installability
- improve prompt bridge and approval flow
- improve self-build executor safety
- improve generated app quality
- improve proof, audit, snapshots, and public repo hygiene
- prepare future desktop, cloud, SaaS, and marketplace modes
