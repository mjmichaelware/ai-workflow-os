
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import datetime
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ["gemini", "claude", "codex"]
SECRET_RE = re.compile(r"(AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,}|ghp_[0-9A-Za-z_]{20,})")


def _redact(value: str) -> str:
    return SECRET_RE.sub("[REDACTED]", value or "")


def should_route_prompt_to_agents(prompt: str) -> bool:
    text = (prompt or "").lower()
    explicit = any(word in text for word in ["agent-routed", "gemini", "claude", "codex", "use agents", "local model cli"])
    lengthy = len(prompt or "") >= 1200
    return explicit or lengthy


def _run(cmd: List[str], timeout: int = 45) -> Dict[str, Any]:
    try:
        run = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "ok": run.returncode == 0,
            "returncode": run.returncode,
            "stdout": _redact(run.stdout)[-12000:],
            "stderr": _redact(run.stderr)[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": 124,
            "stdout": _redact(exc.stdout or ""),
            "stderr": "timeout",
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": 1,
            "stdout": "",
            "stderr": _redact(str(exc)),
        }


def _version(tool: str) -> Dict[str, Any]:
    if shutil.which(tool) is None:
        return {"installed": False, "path": None, "ok": False}
    result = _run([tool, "--version"], timeout=12)
    return {
        "installed": True,
        "path": shutil.which(tool),
        "ok": bool(result.get("ok")),
        "stdout": result.get("stdout", "")[:400],
        "stderr": result.get("stderr", "")[:400],
    }


def _command_for(tool: str, prompt: str) -> List[str] | None:
    if shutil.which(tool) is None:
        return None
    if tool in {"gemini", "claude"}:
        return [tool, "-p", prompt]
    if tool == "codex":
        return None
    return None


def _agent_prompt(user_prompt: str) -> str:
    return (
        "You are helping AI Workflow OS create a generated application. "
        "Return a concise implementation plan only. Do not include secrets. "
        "Do not request broad permissions. Do not include shell commands that install, delete, or exfiltrate files. "
        "Use sections: app_name, screens, data_model, files, tests, safety, packaging. "
        "The output will be saved as an untrusted draft and will not be executed directly.\n\n"
        "User prompt:\n"
        + (user_prompt or "")[:8000]
    )


def route_prompt_to_agents(prompt: str, app_dir: Path) -> Dict[str, Any]:
    app_dir = Path(app_dir)
    drafts = app_dir / "agent_drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    safe_prompt = _agent_prompt(prompt)
    agents = []

    for tool in AGENTS:
        info: Dict[str, Any] = {
            "tool": tool,
            "installed": shutil.which(tool) is not None,
            "used": False,
            "ok": False,
            "reason": None,
        }
        info["version"] = _version(tool)
        cmd = _command_for(tool, safe_prompt)
        if cmd is None:
            info["reason"] = "missing or intentionally unsupported prompt mode"
            agents.append(info)
            continue

        result = _run(cmd, timeout=60)
        info["used"] = True
        info["ok"] = bool(result.get("ok")) or bool(result.get("stdout"))
        info["returncode"] = result.get("returncode")
        info["stdout_chars"] = len(result.get("stdout", ""))
        info["stderr_tail"] = result.get("stderr", "")[-800:]
        draft_path = drafts / f"{tool}_plan.txt"
        draft_path.write_text(result.get("stdout", "") or result.get("stderr", ""), encoding="utf-8")
        info["draft"] = str(draft_path.relative_to(app_dir))
        agents.append(info)

    route = {
        "ok": True,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "prompt_chars": len(prompt or ""),
        "agents": agents,
        "used_agents": [item["tool"] for item in agents if item.get("used")],
        "successful_agents": [item["tool"] for item in agents if item.get("used") and item.get("ok")],
        "keys_printed": False,
        "broad_permissions": False,
        "raw_shell_from_agents_executed": False,
        "drafts_dir": "agent_drafts",
    }
    (drafts / "AGENT_ROUTE.json").write_text(json.dumps(route, indent=2), encoding="utf-8")
    return route


def skipped_agent_route(app_dir: Path, reason: str = "prompt did not request agent routing") -> Dict[str, Any]:
    app_dir = Path(app_dir)
    drafts = app_dir / "agent_drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    route = {
        "ok": True,
        "skipped": True,
        "reason": reason,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "agents": [{"tool": tool, "installed": shutil.which(tool) is not None, "used": False} for tool in AGENTS],
        "used_agents": [],
        "successful_agents": [],
        "keys_printed": False,
        "broad_permissions": False,
        "raw_shell_from_agents_executed": False,
        "drafts_dir": "agent_drafts",
    }
    (drafts / "AGENT_ROUTE.json").write_text(json.dumps(route, indent=2), encoding="utf-8")
    return route


def failed_agent_route(app_dir: Path, error: str) -> Dict[str, Any]:
    app_dir = Path(app_dir)
    drafts = app_dir / "agent_drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    route = {
        "ok": False,
        "error": _redact(error),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "agents": [],
        "used_agents": [],
        "successful_agents": [],
        "keys_printed": False,
        "broad_permissions": False,
        "raw_shell_from_agents_executed": False,
        "drafts_dir": "agent_drafts",
    }
    (drafts / "AGENT_ROUTE.json").write_text(json.dumps(route, indent=2), encoding="utf-8")
    return route


def attach_agent_route_to_manifest(app_dir: Path, route: Dict[str, Any]) -> None:
    app_dir = Path(app_dir)
    manifest_path = app_dir / "APP_MANIFEST.json"
    manifest: Dict[str, Any] = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    manifest["agent_routed_builder_v1"] = {
        "ok": bool(route.get("ok")),
        "skipped": bool(route.get("skipped")),
        "used_agents": route.get("used_agents", []),
        "successful_agents": route.get("successful_agents", []),
        "drafts_dir": route.get("drafts_dir"),
        "keys_printed": False,
        "broad_permissions": False,
        "raw_shell_from_agents_executed": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
