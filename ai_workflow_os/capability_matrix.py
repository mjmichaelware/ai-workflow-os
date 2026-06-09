
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

CAPABILITIES: List[Dict[str, Any]] = [
    {
        "id": "git",
        "label": "Git",
        "kind": "vcs",
        "binary": "git",
        "safe_templates": ["git status --short", "git diff --check", "git log --oneline -5"],
        "writes_repo": True,
        "network": "optional",
        "secret_policy": "never print credentials or remotes with embedded tokens",
        "proof": "git --version",
    },
    {
        "id": "python",
        "label": "Python",
        "kind": "runtime",
        "binary": "python3",
        "safe_templates": ["python3 -m py_compile", "python3 -m pytest -q"],
        "writes_repo": False,
        "network": "none by default",
        "secret_policy": "no environment dump",
        "proof": "python3 --version",
    },
    {
        "id": "pytest",
        "label": "Pytest",
        "kind": "test",
        "binary": "python3",
        "safe_templates": ["PYTHONPATH=$PWD python3 -m pytest -q"],
        "writes_repo": False,
        "network": "none",
        "secret_policy": "redact stdout on failures if token patterns appear",
        "proof": "python3 -m pytest --version",
    },
    {
        "id": "gh",
        "label": "GitHub CLI",
        "kind": "platform-cli",
        "binary": "gh",
        "safe_templates": ["gh auth status", "gh repo view"],
        "writes_repo": False,
        "network": "github",
        "secret_policy": "never print tokens",
        "proof": "gh --version",
    },
    {
        "id": "gcloud",
        "label": "Cloud CLI",
        "kind": "platform-cli",
        "binary": "gcloud",
        "safe_templates": ["gcloud --version", "gcloud config list --format=json"],
        "writes_repo": False,
        "network": "cloud",
        "secret_policy": "never print credentials",
        "proof": "gcloud --version",
    },
    {
        "id": "node",
        "label": "Node",
        "kind": "runtime",
        "binary": "node",
        "safe_templates": ["node --version"],
        "writes_repo": False,
        "network": "none by default",
        "secret_policy": "no environment dump",
        "proof": "node --version",
    },
    {
        "id": "npm",
        "label": "NPM",
        "kind": "package-manager",
        "binary": "npm",
        "safe_templates": ["npm --version", "npm audit --json"],
        "writes_repo": True,
        "network": "registry",
        "secret_policy": "never print npm tokens",
        "proof": "npm --version",
    },
    {
        "id": "gemini",
        "label": "Gemini CLI",
        "kind": "agent",
        "binary": "gemini",
        "safe_templates": ["gemini --version"],
        "writes_repo": "requires explicit task packet",
        "network": "model-provider",
        "secret_policy": "keys only through provider auth, never in scripts",
        "proof": "gemini --version",
    },
    {
        "id": "claude",
        "label": "Claude CLI",
        "kind": "agent",
        "binary": "claude",
        "safe_templates": ["claude --version"],
        "writes_repo": "requires explicit task packet",
        "network": "model-provider",
        "secret_policy": "keys only through provider auth, never in scripts",
        "proof": "claude --version",
    },
    {
        "id": "codex",
        "label": "Codex CLI",
        "kind": "agent",
        "binary": "codex",
        "safe_templates": ["codex --version"],
        "writes_repo": "requires explicit task packet",
        "network": "model-provider",
        "secret_policy": "keys only through provider auth, never in scripts",
        "proof": "codex --version",
    },
    {
        "id": "curl",
        "label": "Curl",
        "kind": "http-client",
        "binary": "curl",
        "safe_templates": ["curl -fsS http://127.0.0.1:8765/"],
        "writes_repo": False,
        "network": "explicit URL only",
        "secret_policy": "never place tokens in URL",
        "proof": "curl --version",
    },
]

def _run_version(command: str) -> Dict[str, Any]:
    parts = command.split()
    binary = parts[0]
    if shutil.which(binary) is None:
        return {"ok": False, "installed": False, "command": command, "stdout": "", "stderr": "missing binary"}
    try:
        run = subprocess.run(parts, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12)
        return {
            "ok": run.returncode == 0,
            "installed": True,
            "command": command,
            "stdout": run.stdout[:800],
            "stderr": run.stderr[:800],
        }
    except Exception as exc:
        return {"ok": False, "installed": True, "command": command, "stdout": "", "stderr": str(exc)}

def build_capability_matrix() -> Dict[str, Any]:
    checked = []
    for item in CAPABILITIES:
        copy = dict(item)
        copy["detected"] = _run_version(str(item["proof"]))
        checked.append(copy)
    payload = {
        "ok": True,
        "local_only_inventory": True,
        "broad_permissions": False,
        "keys_printed": False,
        "capabilities": checked,
    }
    return payload

def write_capability_matrix() -> Dict[str, Any]:
    payload = build_capability_matrix()
    out = ROOT / "docs" / "capabilities" / "TOOL_AGENT_CAPABILITY_MATRIX.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md = ROOT / "docs" / "capabilities" / "TOOL_AGENT_CAPABILITY_MATRIX.md"
    lines = ["# Tool and Agent Capability Matrix", "", "Every tool is treated as a scoped capability, not an unlimited permission.", ""]
    for item in payload["capabilities"]:
        detected = item["detected"]
        status = "installed" if detected.get("installed") else "missing"
        lines.append(f"- **{item['label']}** ({item['kind']}): {status}; network={item['network']}; writes_repo={item['writes_repo']}")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload

if __name__ == "__main__":
    print(json.dumps(write_capability_matrix(), indent=2))
