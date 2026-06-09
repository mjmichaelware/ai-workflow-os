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
    name = "shell-inheritance-proof-" + stamp
    build = request_json("/api/operator/run", {"prompt": "Create an app named " + name + " that proves generated app shell inheritance.", "publish": False})
    apps = build.get("created_apps", [])
    if not build.get("ok") or not apps:
        print(json.dumps({"ok": False, "stage": "operator_run", "build": build}, indent=2))
        return 1
    app = Path(apps[0]["path"])
    required = [
        app / "web" / "index.html",
        app / "web" / "manifest.webmanifest",
        app / "web" / "sw.js",
        app / "web" / "assets" / "app.css",
        app / "web" / "assets" / "app.js",
        app / "web" / "assets" / "icon.svg",
        app / "builder.py",
        app / "android_wrapper" / "android_wrapper.json",
        app / "proof" / "app_shell_proof.json",
        app / "proof" / "app_shell_packet.json",
    ]
    child = subprocess.run([sys.executable, str(app / "builder.py"), "child-from-shell-proof-" + stamp], cwd=app, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ok = all(item.exists() for item in required) and child.returncode == 0
    archive = ARCHIVE_ROOT / ("aiwos_generated_app_shell_proof_" + stamp)
    archive.mkdir(parents=True, exist_ok=True)
    result = {
        "ok": ok,
        "operator_run_ok": bool(build.get("ok")),
        "generated_app": apps[0].get("name"),
        "shell_files_present": all(item.exists() for item in required),
        "child_builder_ok": child.returncode == 0,
        "required_files": [str(item) for item in required],
        "archive": str(archive),
        "keys_printed": False,
    }
    if app.exists():
        shutil.move(str(app), str(archive / app.name))
    print(json.dumps(result, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
