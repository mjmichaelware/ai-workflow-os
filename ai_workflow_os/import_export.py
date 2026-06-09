from __future__ import annotations

from pathlib import Path
import json
import time

def export_app_manifest(target: Path, out: Path) -> Path:
    target = target.resolve()
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(target.glob("**/*")):
        if path.is_file():
            rel = str(path.relative_to(target))
            if ".git/" not in rel and "__pycache__" not in rel:
                try:
                    files.append({"path": rel, "text": path.read_text()})
                except UnicodeDecodeError:
                    files.append({"path": rel, "binary_skipped": True})
    out.write_text(json.dumps({"exported_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "source": str(target), "files": files}, indent=2))
    return out

def import_app_manifest(manifest: Path, target: Path, execute: bool = False) -> dict:
    data = json.loads(manifest.read_text())
    target = target.resolve()
    planned = [item["path"] for item in data.get("files", []) if not item.get("binary_skipped")]
    if not execute:
        return {"target": str(target), "execute": False, "planned_files": planned}
    written = []
    for item in data.get("files", []):
        if item.get("binary_skipped"):
            continue
        path = target / item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item.get("text", ""))
        written.append(item["path"])
    return {"target": str(target), "execute": True, "written": written}
