from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = Path.home() / "tmp"

def request_json(path: str, payload: dict | None = None) -> dict:
    url = "http://127.0.0.1:8765" + path
    if payload is None:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=240) as response:
        return json.loads(response.read().decode("utf-8"))

def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    parent_name = "recursive-builder-proof-" + stamp
    child_name = "child-built-by-generated-app-" + stamp
    prompt = "Create an app named " + parent_name + " that can build a child application from a terminal command."
    build = request_json("/api/operator/run", {"prompt": prompt, "publish": False})
    created = build.get("created_apps", [])
    if not build.get("ok") or not created:
        print(json.dumps({"ok": False, "stage": "operator_run", "build": build}, indent=2))
        return 1
    parent = Path(created[0]["path"])
    builder = parent / "builder.py"
    run = subprocess.run([sys.executable, str(builder), child_name], cwd=parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        child_result = json.loads(run.stdout)
    except Exception:
        child_result = {"ok": False, "stdout": run.stdout, "stderr": run.stderr}
    child_path = Path(child_result.get("path", parent / "children" / child_name))
    required = [child_path / "README.md", child_path / "app.py", child_path / "APP_MANIFEST.json"]
    archive = ARCHIVE_ROOT / ("aiwos_recursive_factory_proof_" + stamp)
    archive.mkdir(parents=True, exist_ok=True)
    child_created = all(item.exists() for item in required)
    ok = run.returncode == 0 and bool(child_result.get("ok")) and child_created
    result = {
        "ok": ok,
        "operator_run_ok": bool(build.get("ok")),
        "parent_generated_app": created[0].get("name"),
        "generated_app_builder_executed": run.returncode == 0,
        "child_app_created": child_created,
        "child_files": [str(item) for item in required],
        "archive": str(archive),
        "keys_printed": False,
    }
    if parent.exists():
        shutil.move(str(parent), str(archive / parent.name))
    print(json.dumps(result, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
