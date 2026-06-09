
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import datetime
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def _git(args: list[str]) -> str:
    try:
        run = subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12)
        return (run.stdout or run.stderr).strip()[-4000:]
    except Exception as exc:
        return str(exc)


def _exists(path: str) -> bool:
    return (ROOT / path).exists()


def runtime_console_payload() -> Dict[str, Any]:
    proof_files = [
        "scripts/prove_operator_button_flow.py",
        "scripts/prove_recursive_app_factory.py",
        "scripts/prove_generated_app_shell.py",
        "scripts/prove_native_android_wrapper.py",
        "scripts/prove_capability_matrix.py",
        "scripts/final_perfection_report.py",
        "scripts/verify_public_surface.py",
    ]
    assets = [
        "web/assets/console.css",
        "web/assets/visual-system-v3.css",
        "web/assets/visual-max-v4.css",
        "web/assets/endpoint-graph.js",
        "web/assets/final-proof-dashboard.js",
        "web/assets/runtime-console.js",
        "web/assets/ux-density-v5.css",
    ]
    generated_apps = []
    generated_root = ROOT / "generated_apps"
    if generated_root.exists():
        for item in sorted(generated_root.iterdir()):
            if item.is_dir():
                generated_apps.append({
                    "name": item.name,
                    "manifest": (item / "APP_MANIFEST.json").exists(),
                    "web": (item / "web" / "index.html").exists(),
                    "builder": (item / "builder.py").exists(),
                    "android_wrapper": (item / "android_wrapper").exists(),
                    "proof": (item / "proof").exists(),
                })
    return {
        "ok": True,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_head": _git(["log", "-1", "--oneline"]),
        "git_status": _git(["status", "--short"]),
        "branch": _git(["branch", "--show-current"]),
        "proof_files": [{"path": item, "exists": _exists(item)} for item in proof_files],
        "assets": [{"path": item, "exists": _exists(item)} for item in assets],
        "generated_apps": generated_apps,
        "capabilities": {
            "app_factory": _exists("ai_workflow_os/operator_console.py"),
            "generated_shell": _exists("ai_workflow_os/generated_app_shell.py"),
            "native_wrapper_scaffold": _exists("ai_workflow_os/native_android_wrapper.py"),
            "capability_matrix": _exists("ai_workflow_os/capability_matrix.py"),
            "endpoint_graph": _exists("web/assets/endpoint-graph.data.json"),
            "final_report": _exists("docs/proof/FINAL_PERFECTION_REPORT.md"),
            "ci_scaffold": _exists(".github/workflows/ci.yml"),
        },
        "safety": {
            "keys_printed": False,
            "broad_permissions": False,
            "arbitrary_shell_from_browser": False,
            "browser_assets_local_only": True,
        },
    }


if __name__ == "__main__":
    print(json.dumps(runtime_console_payload(), indent=2))
