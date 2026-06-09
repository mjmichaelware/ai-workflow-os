
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_workflow_os.native_android_wrapper import export_native_android_wrapper


def main() -> int:
    result = export_native_android_wrapper("AI Workflow OS", "http://127.0.0.1:8765/")
    path = Path(result["path"])
    required = [
        "WRAPPER_MANIFEST.json",
        "README.md",
        "settings.gradle",
        "build.gradle",
        "app/build.gradle",
        "app/src/main/AndroidManifest.xml",
        "app/src/main/res/values/styles.xml",
        "app/src/main/res/drawable/launcher_icon.xml",
        "proof/native_wrapper_proof.json",
    ]
    missing = [rel for rel in required if not (path / rel).exists()]
    manifest = json.loads((path / "WRAPPER_MANIFEST.json").read_text(encoding="utf-8"))
    ok = not missing and result.get("ok") and manifest.get("broad_permissions") is False and manifest.get("keys_printed") is False
    proof = {
        "ok": bool(ok),
        "path": str(path),
        "missing": missing,
        "package": result.get("package"),
        "keys_printed": False,
        "broad_permissions": False,
    }
    print(json.dumps(proof, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
