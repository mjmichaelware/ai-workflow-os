
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from datetime import datetime, timezone
import json
import os
import shutil
import subprocess
import uuid

from .prompt_bridge import submit_prompt, approve_prompt, complete_prompt
from .self_build_executor import run_next_self_build
from .phone_wrapper import export_phone_bundle

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "ai_workflow_os" / "operator_runs"

CLI_TOOLS = {
    "gemini": "gemini",
    "claude": "claude",
    "codex": "codex",
    "aider": "aider",
    "gh": "gh",
    "gcloud": "gcloud",
    "vercel": "vercel",
    "supabase": "supabase",
    "node": "node",
    "npm": "npm",
    "python": "python3",
    "git": "git"
}

SECRET_ENV = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "TOGETHER_API_KEY",
    "SERPAPI_API_KEY",
    "GITHUB_TOKEN",
    "VERCEL_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY"
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def run(cmd: list[str], timeout: int = 180) -> Dict[str, Any]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, shell=False)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:]
    }

def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + chr(10), encoding="utf-8")

def tool_inventory() -> Dict[str, Any]:
    tools = {}
    for name, command in CLI_TOOLS.items():
        tools[name] = {
            "installed": shutil.which(command) is not None,
            "path": shutil.which(command)
        }
    env = {name: bool(os.environ.get(name)) for name in SECRET_ENV}
    return {
        "ok": True,
        "tools": tools,
        "secret_env_presence_only": env,
        "keys_are_not_stored_or_printed": True
    }

def operator_manifest() -> Dict[str, Any]:
    return {
        "ok": True,
        "name": "AI Workflow OS Operator Console",
        "purpose": "Phone-first prompt interface that drives Termux, approved self-builds, exports, and Git proof",
        "local_url": "http://127.0.0.1:8765",
        "raw_shell": False,
        "repo_scoped": True,
        "uses_existing_termux_cli_auth": True,
        "stores_keys": False,
        "prints_keys": False,
        "endpoints": [
            "/api/operator/manifest",
            "/api/operator/status",
            "/api/operator/run",
            "/api/operator/publish"
        ],
        "flow": [
            "phone prompt",
            "prompt bridge",
            "approval",
            "self-build executor",
            "compile and tests",
            "phone export",
            "optional GitHub publish"
        ]
    }

def operator_run(prompt: str, publish: bool = False) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    prompt = (prompt or "").strip()
    if not prompt:
        return {"ok": False, "error": "empty prompt"}

    submitted = submit_prompt(prompt, "operator-console", "self_build")
    if not submitted.get("ok"):
        return submitted

    approved = approve_prompt(submitted["id"], True)
    build = run_next_self_build()
    exported = export_phone_bundle()

    result = {
        "ok": bool(build.get("ok") and exported.get("ok")),
        "run_id": run_id,
        "prompt_id": submitted["id"],
        "prompt": prompt,
        "submitted": submitted,
        "approved": approved,
        "build": build,
        "export": exported,
        "tool_inventory": tool_inventory(),
        "published": None,
        "created_at": now()
    }

    if publish:
        result["published"] = operator_publish("Operator build")

    complete_prompt(submitted["id"], result)
    write_json(RUN_DIR / (run_id + ".json"), result)
    return result

def operator_publish(message: str = "Operator build") -> Dict[str, Any]:
    compile_result = run(["python3", "-m", "compileall", "-q", "ai_workflow_os"], timeout=180)
    test_result = run(["python3", "-m", "pytest", "tests/test_registry_spine.py", "tests/test_app_pumps.py", "tests/test_terminal_bridge.py", "tests/test_prompt_bridge.py", "tests/test_self_build_executor.py", "tests/test_phone_wrapper.py", "-q"], timeout=240)
    diff_result = run(["git", "diff", "--check"], timeout=60)

    if not (compile_result["ok"] and test_result["ok"] and diff_result["ok"]):
        return {
            "ok": False,
            "stage": "prepublish",
            "compile": compile_result,
            "tests": test_result,
            "diff": diff_result
        }

    add_result = run(["git", "add", "ai_workflow_os", "web", "bin", "scripts", "docs", "tests", "generated_apps"], timeout=120)
    commit_result = run(["git", "commit", "-m", message], timeout=120)
    push_result = run(["git", "push", "-u", "origin", subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()], timeout=240)

    return {
        "ok": push_result["ok"] or "nothing to commit" in commit_result.get("stdout", "").lower() or "nothing to commit" in commit_result.get("stderr", "").lower(),
        "compile": compile_result,
        "tests": test_result,
        "diff": diff_result,
        "add": add_result,
        "commit": commit_result,
        "push": push_result
    }

def operator_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "manifest": operator_manifest(),
        "inventory": tool_inventory(),
        "phone_export_exists": (Path.home() / "storage" / "downloads" / "AI_WORKFLOW_OS_PHONE_WRAPPER.zip").exists()
    }
