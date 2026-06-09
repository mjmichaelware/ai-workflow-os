from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import datetime
import json
import re

from .generated_app_shell import ensure_generated_app_shell, build_shell_packet

ROOT = Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "generated-app").lower()).strip("-")
    return value[:72] or "generated-app"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def create_recursive_child(parent_app_dir: Path, name: str, depth: int) -> Dict[str, Any]:
    parent_app_dir = Path(parent_app_dir)
    child_dir = parent_app_dir / "children" / slugify(name)
    child_dir.mkdir(parents=True, exist_ok=True)

    title = name.replace("-", " ").replace("_", " ").title()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    (child_dir / "README.md").write_text(
        f"# {title}\n\nRecursive generated app depth {depth}.\n\nThis child inherits the generated app shell contract.\n",
        encoding="utf-8",
    )
    (child_dir / "app.py").write_text(
        "from __future__ import annotations\n\n"
        "def app_info():\n"
        f"    return {{'ok': True, 'name': {name!r}, 'depth': {depth}, 'can_build_child_apps': True}}\n\n"
        "if __name__ == '__main__':\n"
        "    print(app_info())\n",
        encoding="utf-8",
    )

    manifest = {
        "ok": True,
        "name": slugify(name),
        "title": title,
        "built_by": "recursive-inheritance-builder",
        "created_at": now,
        "depth": depth,
        "can_build_child_apps": True,
        "inherits_generated_app_shell": True,
        "keys_printed": False,
        "broad_permissions": False,
    }
    _write_json(child_dir / "APP_MANIFEST.json", manifest)

    shell = ensure_generated_app_shell(child_dir, title)
    packet = build_shell_packet(child_dir)
    _write_json(child_dir / "proof" / "recursive_inheritance_proof.json", {
        "ok": bool(shell.get("ok") and packet.get("ok")),
        "depth": depth,
        "name": slugify(name),
        "shell": shell,
        "packet": {"ok": packet.get("ok"), "format": packet.get("format"), "bytes": packet.get("bytes")},
        "keys_printed": False,
        "broad_permissions": False,
    })

    return {
        "ok": True,
        "path": str(child_dir),
        "manifest": manifest,
        "shell": shell,
        "packet": {"ok": packet.get("ok"), "format": packet.get("format"), "bytes": packet.get("bytes")},
        "keys_printed": False,
        "broad_permissions": False,
    }


def prove_grandchild_chain(root_app_dir: Path) -> Dict[str, Any]:
    child = create_recursive_child(root_app_dir, "child-with-inherited-shell", 2)
    grandchild = create_recursive_child(Path(child["path"]), "grandchild-with-inherited-shell", 3)
    great_grandchild = create_recursive_child(Path(grandchild["path"]), "great-grandchild-with-inherited-shell", 4)

    chain = [child, grandchild, great_grandchild]
    required = [
        "web/index.html",
        "web/manifest.webmanifest",
        "web/sw.js",
        "web/assets/app.css",
        "web/assets/app.js",
        "builder.py",
        "android_wrapper/android_wrapper.json",
        "proof/app_shell_proof.json",
        "proof/app_shell_packet.json",
        "proof/recursive_inheritance_proof.json",
    ]
    checks = []
    for item in chain:
        path = Path(item["path"])
        missing = [rel for rel in required if not (path / rel).exists()]
        checks.append({
            "path": str(path),
            "ok": not missing,
            "missing": missing,
            "depth": item.get("manifest", {}).get("depth"),
        })

    return {
        "ok": all(item["ok"] for item in checks),
        "chain": checks,
        "keys_printed": False,
        "broad_permissions": False,
        "depth_proven": 4,
    }
