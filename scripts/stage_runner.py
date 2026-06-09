from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "storage/downloads"
TMP = Path.home() / "tmp"

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout)
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result

def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)

def chmod_x(path: str) -> None:
    target = ROOT / path
    target.chmod(target.stat().st_mode | 0o755)

def ensure_dirs() -> None:
    for path in [
        "ai_workflow_os",
        "web/static",
        "generated_apps",
        "android_targets",
        "runs",
        "approvals",
        "docs",
        "stages",
    ]:
        (ROOT / path).mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

def verify() -> None:
    run(["python3", "-m", "py_compile", *[str(p) for p in sorted((ROOT / "ai_workflow_os").glob("*.py"))]])
    run(["bash", "scripts/verify_workflow_app.sh"])
    run(["bin/ai-workflow-os", "doctor"])
    run(["bin/ai-workflow-os", "tools"])
    run(["bin/ai-workflow-os", "list-apps"])
    run(["bin/ai-workflow-os", "android-status"])

def commit_push(message: str) -> None:
    run(["git", "add", "-A"])
    diff = run(["git", "diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        print("No changes to commit.")
    else:
        run(["git", "commit", "-m", message])
    remote = run(["git", "remote", "get-url", "origin"], check=False)
    if remote.returncode == 0:
        branch = run(["git", "branch", "--show-current"]).stdout.strip()
        run(["git", "push", "-u", "origin", branch])
    else:
        print("No origin remote configured; commit is local.")

def restart_dashboard(port: int = 8765) -> None:
    run(["pkill", "-f", "ai_workflow_os.cli serve"], check=False)
    run(["pkill", "-f", "scripts/run_dashboard.sh"], check=False)
    log = TMP / "ai_workflow_os_dashboard.log"
    pid = TMP / "ai_workflow_os_dashboard.pid"
    proc = subprocess.Popen(
        ["bin/ai-workflow-os", "serve", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(ROOT),
        stdout=log.open("w"),
        stderr=subprocess.STDOUT,
    )
    pid.write_text(str(proc.pid))
    time.sleep(2)
    print(f"Dashboard PID: {proc.pid}")
    print(log.read_text()[-4000:] if log.exists() else "")
    print(f"OPEN: http://127.0.0.1:{port}/?t={int(time.time())}")

def stage_status() -> None:
    print(json.dumps({
        "root": str(ROOT),
        "downloads": str(DOWNLOADS),
        "git": shutil.which("git") is not None,
        "gh": shutil.which("gh") is not None,
        "gcloud": shutil.which("gcloud") is not None,
        "python3": shutil.which("python3") is not None,
        "node": shutil.which("node") is not None,
        "npm": shutil.which("npm") is not None,
        "java": shutil.which("java") is not None,
        "gradle": shutil.which("gradle") is not None,
        "android_home": bool(os.environ.get("ANDROID_HOME")),
    }, indent=2))

def stage_export_demo() -> None:
    run([
        "bin/ai-workflow-os",
        "create-app",
        "Create an app that helps me manage projects from my phone terminal with APIs, CLI tools, browser UI, import export, native targets, and tests.",
        "--target",
        "generated_apps/phone-project-agent",
        "--name",
        "phone-project-agent",
        "--execute",
    ])
    run(["bin/ai-workflow-os", "test-app", "generated_apps/phone-project-agent"])
    run(["bin/ai-workflow-os", "export-app-downloads", "phone-project-agent"])
    run(["bin/ai-workflow-os", "android-target", "phone-project-agent", "Create a native Android build target for the phone project agent."])

def stage_secure_vault_plan() -> None:
    write("docs/SECURE_LOCAL_VAULT_PLAN.md", """# Secure Local Vault Plan

Goal: let AI Workflow OS ingest local credential documents safely without uploading secret values to model providers.

Rules:
- Secret values are never printed.
- Secret values are never committed.
- Secret values are never sent to LLM APIs.
- Documents are parsed locally.
- Candidate secret names are extracted locally.
- User approves each secret before storing it.
- Cloud storage target is Google Secret Manager when available.
- Local fallback is an encrypted vault file, not plaintext.

Required modules:
- vault_ingest.py
- vault_store.py
- oauth_runner.py
- provider_handshake.py
- secret_audit.py

Required UI:
- Vault tab
- Import document button
- Redacted preview
- Approve-to-store action
- Secret Manager existence check
- OAuth flow status
""")
    write("stages/06_secure_vault.json", json.dumps({
        "stage": "06_secure_vault",
        "purpose": "secure local credential/document ingestion and OAuth runner",
        "status": "planned",
        "side_effects": "none",
        "secret_values_printed": False
    }, indent=2) + "\n")

def main() -> int:
    ensure_dirs()
    stage = sys.argv[1] if len(sys.argv) > 1 else "status"

    if stage == "status":
        stage_status()
        return 0
    if stage == "verify":
        verify()
        return 0
    if stage == "export-demo":
        stage_export_demo()
        verify()
        commit_push("Verify app factory demo export and native target")
        restart_dashboard()
        return 0
    if stage == "secure-vault-plan":
        stage_secure_vault_plan()
        verify()
        commit_push("Plan secure local vault and OAuth ingestion layer")
        restart_dashboard()
        return 0
    if stage == "restart":
        restart_dashboard()
        return 0
    if stage == "ship":
        verify()
        commit_push("Ship verified AI Workflow OS state")
        restart_dashboard()
        return 0

    print("Unknown stage:", stage)
    print("Available: status, verify, export-demo, secure-vault-plan, restart, ship")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
