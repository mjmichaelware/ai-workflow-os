from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import os
import shutil
import subprocess
from typing import Dict, List


@dataclass
class ToolResult:
    tool: str
    ok: bool
    command: List[str]
    stdout: str
    stderr: str
    returncode: int
    executed: bool
    note: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _run(tool: str, cmd: List[str], cwd: Path | None = None, execute: bool = False, timeout: int = 60) -> ToolResult:
    if not execute:
        return ToolResult(tool, True, cmd, "", "", 0, False, "dry_run: command recorded but not executed")
    try:
        result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return ToolResult(tool, result.returncode == 0, cmd, result.stdout[-8000:], result.stderr[-8000:], result.returncode, True, "executed")
    except subprocess.TimeoutExpired as exc:
        return ToolResult(tool, False, cmd, exc.stdout or "", exc.stderr or "", 124, True, "timeout")
    except Exception as exc:
        return ToolResult(tool, False, cmd, "", str(exc), 1, True, "exception")


class RepoInspector:
    def inspect(self, target: Path) -> Dict[str, object]:
        target = target.resolve()
        files = []
        for path in sorted(target.glob("**/*")):
            if path.is_file():
                rel = str(path.relative_to(target))
                if ".git/" not in rel and "__pycache__" not in rel and "node_modules/" not in rel:
                    files.append(rel)
                if len(files) >= 500:
                    break
        return {
            "target": str(target),
            "has_git": (target / ".git").exists(),
            "file_count_sampled": len(files),
            "files": files,
            "manifests": {
                "pyproject": (target / "pyproject.toml").exists(),
                "package_json": (target / "package.json").exists(),
                "requirements": (target / "requirements.txt").exists(),
                "dockerfile": (target / "Dockerfile").exists(),
            },
        }


class FileTool:
    def write_text(self, path: Path, text: str, execute: bool = False) -> ToolResult:
        cmd = ["write-file", str(path)]
        if not execute:
            return ToolResult("file", True, cmd, "", "", 0, False, "dry_run: file write recorded")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return ToolResult("file", True, cmd, f"wrote {path}", "", 0, True, "executed")


class ShellTool:
    def run(self, cmd: List[str], cwd: Path | None = None, execute: bool = False) -> ToolResult:
        blocked = {"rm", "sudo", "su", "reboot", "shutdown", "mkfs", "dd"}
        if cmd and cmd[0] in blocked:
            return ToolResult("shell", False, cmd, "", "blocked dangerous command", 126, False, "blocked")
        return _run("shell", cmd, cwd=cwd, execute=execute, timeout=120)


class GitTool:
    def status(self, cwd: Path, execute: bool = False) -> ToolResult:
        return _run("git", ["git", "status", "--short"], cwd=cwd, execute=execute)

    def diff_stat(self, cwd: Path, execute: bool = False) -> ToolResult:
        return _run("git", ["git", "--no-pager", "diff", "--stat"], cwd=cwd, execute=execute)

    def commit(self, cwd: Path, message: str, execute: bool = False) -> ToolResult:
        return _run("git", ["git", "commit", "-m", message], cwd=cwd, execute=execute)


class GhTool:
    def status(self, cwd: Path, execute: bool = False) -> ToolResult:
        if shutil.which("gh") is None:
            return ToolResult("gh", False, ["gh", "auth", "status"], "", "gh not installed", 127, False, "missing")
        return _run("gh", ["gh", "auth", "status"], cwd=cwd, execute=execute)


class GcloudTool:
    def config_project(self, execute: bool = False) -> ToolResult:
        if shutil.which("gcloud") is None:
            return ToolResult("gcloud", False, ["gcloud", "config", "get-value", "project"], "", "gcloud not installed", 127, False, "missing")
        return _run("gcloud", ["gcloud", "config", "get-value", "project"], execute=execute)

    def secret_describe(self, secret_name: str, project: str | None = None, execute: bool = False) -> ToolResult:
        if shutil.which("gcloud") is None:
            return ToolResult("gcloud", False, ["gcloud"], "", "gcloud not installed", 127, False, "missing")
        cmd = ["gcloud", "secrets", "describe", secret_name, "--quiet"]
        if project:
            cmd += ["--project", project]
        return _run("gcloud", cmd, execute=execute)


def tool_inventory() -> Dict[str, object]:
    return {
        "git": shutil.which("git") is not None,
        "gh": shutil.which("gh") is not None,
        "gcloud": shutil.which("gcloud") is not None,
        "python3": shutil.which("python3") is not None,
        "node": shutil.which("node") is not None,
        "npm": shutil.which("npm") is not None,
        "rg": shutil.which("rg") is not None,
        "jq": shutil.which("jq") is not None,
    }
