from __future__ import annotations

from pathlib import Path
import time

from .app_builder import test_generated_app

def list_generated_apps(repo_root: Path) -> dict:
    root = repo_root.resolve() / "generated_apps"
    root.mkdir(parents=True, exist_ok=True)
    apps = []
    for item in sorted(root.iterdir()):
        if item.is_dir():
            apps.append({
                "name": item.name,
                "path": str(item),
                "has_app_py": (item / "app.py").exists(),
                "has_web_ui": (item / "web/index.html").exists(),
                "has_test": (item / "scripts/test.sh").exists()
            })
    return {"generated_root": str(root), "apps": apps}

def test_app_by_name(repo_root: Path, name: str) -> dict:
    path = repo_root.resolve() / "generated_apps" / name
    if not path.exists():
        return {"ok": False, "error": "generated app not found", "name": name, "path": str(path)}
    return test_generated_app(path)

def export_app_to_downloads(repo_root: Path, name: str, downloads_dir: Path) -> dict:
    app_path = repo_root.resolve() / "generated_apps" / name
    downloads_dir.mkdir(parents=True, exist_ok=True)
    if not app_path.exists():
        return {"ok": False, "error": "generated app not found", "name": name, "path": str(app_path)}
    out = downloads_dir / f"AI_WORKFLOW_OS_{name}_source_bundle.txt"
    lines = ["# AI Workflow OS Generated App Export", "", f"Exported at: {time.strftime(chr(37)+chr(89)+chr(45)+chr(37)+chr(109)+chr(45)+chr(37)+chr(100)+chr(84)+chr(37)+chr(72)+chr(58)+chr(37)+chr(77)+chr(58)+chr(37)+chr(83)+chr(37)+chr(122))}", f"App name: {name}", f"Path: {app_path}", ""]
    for p in sorted(app_path.glob("**/*")):
        if p.is_file() and "__pycache__" not in str(p):
            lines.append("\n" + "=" * 80)
            lines.append("FILE: " + str(p.relative_to(app_path)))
            lines.append("=" * 80)
            lines.append(p.read_text(errors="replace"))
    out.write_text("\n".join(lines) + "\n")
    return {"ok": True, "text_bundle_path": str(out), "downloadable_on_phone": True}
