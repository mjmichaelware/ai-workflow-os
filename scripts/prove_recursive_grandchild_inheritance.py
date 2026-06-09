from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_workflow_os.recursive_inheritance import prove_grandchild_chain


def request_json(path: str, payload: dict | None = None) -> dict:
    url = "http://127.0.0.1:8765" + path
    if payload is None:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    prompt = "Create recursive grandchild inheritance root app " + stamp + " with shell inheritance proof."
    build = request_json("/api/operator/run", {"prompt": prompt, "publish": False})
    apps = build.get("created_apps", [])
    if not build.get("ok") or not apps:
        print(json.dumps({"ok": False, "stage": "operator_run", "build": build}, indent=2))
        return 1

    root_app = Path(apps[0]["path"])
    chain = prove_grandchild_chain(root_app)
    archive = Path.home() / "tmp" / ("aiwos_recursive_grandchild_inheritance_" + stamp)
    archive.mkdir(parents=True, exist_ok=True)

    result = {
        "ok": chain.get("ok") is True,
        "root_app": root_app.name,
        "depth_proven": chain.get("depth_proven"),
        "chain": chain.get("chain", []),
        "keys_printed": False,
        "broad_permissions": False,
        "archive": str(archive),
    }

    if root_app.exists():
        shutil.move(str(root_app), str(archive / root_app.name))

    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
