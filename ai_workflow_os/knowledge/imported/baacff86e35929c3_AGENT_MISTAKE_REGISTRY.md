# Agent Mistake Registry\n\n## 2026-06-08 — Script path import failure

Failure:
- A generated script under `scripts/` imported `ai_workflow_os`.
- It was executed as `python3 scripts/registry_spine.py`.
- Python placed `scripts/` on `sys.path`, not the repo root.
- The script failed with `ModuleNotFoundError: No module named ai_workflow_os`.

Rule:
- Every generated executable Python script inside a subfolder must either:
  1. insert the repo root into `sys.path`, or
  2. be run with `PYTHONPATH="$PWD"`, or
  3. be installed as a package/module command.

Test:
- Run the script the exact way the user will run it.
- Do not count `py_compile` as proof that imports work at runtime.

Judgment:
- Compile proof is not runtime proof.
- Runtime invocation proof is required.
\n
## 2026-06-08 — Module/package name collision

Failure:
- Existing app had `ai_workflow_os/core.py`.
- New registry code created `ai_workflow_os/core/`.
- Python imported the package folder instead of the old module file.
- Existing CLI broke because `from ai_workflow_os.core import scan_project` no longer resolved to `core.py`.

Rule:
- Never create a package directory with the same basename as an existing module file.
- Before adding a package, check `find package -maxdepth 2 -type f` and import users.
- Additive architecture must not shadow existing public modules.

Correct pattern:
- Put new subsystem in a non-conflicting package, such as `ai_workflow_os/registry_spine/`.
- Prove both old CLI and new subsystem import at runtime.

Judgment:
- Compile proof is not enough.
- New architecture must preserve old public API.


## 2026-06-08 — Heredoc with Markdown fence continuation trap

Failure:
- A core build command used heredoc to write Markdown containing fence text.
- Termux entered the continuation prompt instead of completing the action.

Rule:
- Never use heredoc for core OS construction.
- Use staged scripts, Python writers, registry actions, or committed files.
- Every generated app must inherit this same prevention rule.

Judgment:
- If the shell waits at the continuation prompt, the action failed materially.
- The OS must prevent that pattern before generating future apps.
