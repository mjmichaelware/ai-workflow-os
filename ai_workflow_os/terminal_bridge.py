
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "ai_workflow_os" / "terminal_bridge_logs"
PROOF_DIR = ROOT / "ai_workflow_os" / "proofs"

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\\-]{12,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_\\-]{12,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{12,}"),
    re.compile(r"gsk_[A-Za-z0-9_]{12,}"),
    re.compile(r"vcp_[A-Za-z0-9_]{12,}"),
    re.compile(r"tgp_v1_[A-Za-z0-9_\\-]{12,}"),
    re.compile(r"AIza[A-Za-z0-9_\\-]{12,}"),
    re.compile(r"postgresql://[^\\s]+", re.IGNORECASE),
]

COMMANDS: Dict[str, Dict[str, Any]] = {
    "pwd": {"label": "Print repo path", "cmd": ["pwd"], "timeout": 10},
    "git.status": {"label": "Git status", "cmd": ["git", "status", "--short"], "timeout": 20},
    "git.log": {"label": "Recent commits", "cmd": ["git", "log", "--oneline", "--decorate", "-8"], "timeout": 20},
    "os.doctor": {"label": "AI Workflow OS doctor", "cmd": ["bin/ai-workflow-os", "doctor"], "timeout": 30},
    "os.tools": {"label": "CLI tool inventory", "cmd": ["bin/ai-workflow-os", "tools"], "timeout": 30},
    "os.list_apps": {"label": "Generated apps", "cmd": ["bin/ai-workflow-os", "list-apps"], "timeout": 30},
    "registry.manifest": {"label": "Registry manifest", "cmd": ["python3", "scripts/registry_spine.py", "manifest"], "timeout": 30},
    "registry.health": {"label": "Registry health action", "cmd": ["python3", "scripts/registry_spine.py", "dispatch", "system.health", "{}"], "timeout": 30},
    "registry.rebuild": {"label": "Rebuild registries", "cmd": ["python3", "scripts/registry_spine.py", "rebuild"], "timeout": 60},
    "verify.compile": {"label": "Compile Python", "cmd": ["python3", "-m", "compileall", "-q", "ai_workflow_os"], "timeout": 120},
    "verify.tests": {"label": "Run AI Workflow OS tests", "cmd": ["python3", "-m", "pytest", "tests/test_registry_spine.py", "tests/test_app_pumps.py", "-q"], "timeout": 120},
    "verify.workflow": {"label": "Verify workflow app", "cmd": ["bash", "scripts/verify_workflow_app.sh"], "timeout": 120},
    "gh.status": {"label": "GitHub auth status", "cmd": ["gh", "auth", "status"], "timeout": 30, "optional": True},
    "gcloud.account": {"label": "Google Cloud active account", "cmd": ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"], "timeout": 30, "optional": True},
    "gcloud.project": {"label": "Google Cloud project", "cmd": ["gcloud", "config", "get-value", "project"], "timeout": 30, "optional": True},
    "node.version": {"label": "Node version", "cmd": ["node", "--version"], "timeout": 20, "optional": True},
    "npm.version": {"label": "NPM version", "cmd": ["npm", "--version"], "timeout": 20, "optional": True},
    "termux.pkg.list": {"label": "Termux installed package sample", "cmd": ["sh", "-lc", "pkg list-installed | head -80"], "timeout": 30, "optional": True},
}

SENSITIVE_ENV_NAMES = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "TOGETHER_API_KEY",
    "SERPAPI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "VERCEL_TOKEN",
    "GITHUB_TOKEN",
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def redact(text: str) -> str:
    out = text or ""
    for pattern in SECRET_PATTERNS:
        out = pattern.sub("[REDACTED_SECRET]", out)
    for name in SENSITIVE_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            out = out.replace(value, "[REDACTED_" + name + "]")
    return out

def append_jsonl(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, sort_keys=True, default=str) + chr(10))

def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + chr(10), encoding="utf-8")

def list_terminal_commands() -> Dict[str, Any]:
    return {
        "ok": True,
        "policy": "allowlisted commands only, no arbitrary shell, no secret printing",
        "count": len(COMMANDS),
        "commands": [
            {"id": key, "label": value["label"], "cmd_preview": value["cmd"]}
            for key, value in sorted(COMMANDS.items())
        ],
        "secret_env_presence": {
            name: bool(os.environ.get(name))
            for name in SENSITIVE_ENV_NAMES
        },
    }

def run_terminal_command(command_id: str) -> Dict[str, Any]:
    if command_id not in COMMANDS:
        return {"ok": False, "error": "unknown command", "known_commands": sorted(COMMANDS)}

    spec = COMMANDS[command_id]
    run_id = str(uuid.uuid4())
    started = now()

    try:
        proc = subprocess.run(
            spec["cmd"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=int(spec.get("timeout", 30)),
            shell=False,
        )
        result = {
            "ok": proc.returncode == 0,
            "run_id": run_id,
            "command_id": command_id,
            "label": spec["label"],
            "cmd": spec["cmd"],
            "returncode": proc.returncode,
            "stdout": redact(proc.stdout[-12000:]),
            "stderr": redact(proc.stderr[-12000:]),
            "started_at": started,
            "finished_at": now(),
        }
        if spec.get("optional") and proc.returncode != 0:
            result["ok"] = True
            result["optional_warning"] = "optional CLI not authenticated or unavailable"
    except Exception as exc:
        result = {
            "ok": False,
            "run_id": run_id,
            "command_id": command_id,
            "label": spec.get("label", command_id),
            "cmd": spec.get("cmd", []),
            "error": redact(str(exc)),
            "started_at": started,
            "finished_at": now(),
        }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    append_jsonl(LOG_DIR / "terminal_runs.jsonl", result)
    proof_path = PROOF_DIR / (now().replace(":", "-") + "_terminal_" + command_id.replace(".", "_") + ".json")
    write_json(proof_path, result)
    result["proof_path"] = str(proof_path)
    return result
