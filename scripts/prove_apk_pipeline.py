from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_workflow_os.apk_pipeline import create_apk_pipeline_scaffold, detect_android_toolchain, apk_signing_env_contract


def main() -> int:
    scaffold = create_apk_pipeline_scaffold("AI Workflow OS")
    path = Path(scaffold["path"])
    required = [
        "README.md",
        "build_apk.sh",
        "sign_apk.sh",
        "verify_apk.sh",
        "APK_PIPELINE_MANIFEST.json",
    ]
    missing = [rel for rel in required if not (path / rel).exists()]
    manifest = json.loads((path / "APK_PIPELINE_MANIFEST.json").read_text(encoding="utf-8"))
    ok = (
        not missing
        and manifest.get("keys_printed") is False
        and manifest.get("broad_permissions") is False
        and manifest.get("keystore_in_repo") is False
        and detect_android_toolchain().get("ok") is True
        and apk_signing_env_contract().get("values_printed") is False
    )
    result = {
        "ok": bool(ok),
        "path": str(path),
        "missing": missing,
        "toolchain": manifest.get("toolchain", {}),
        "signing_contract_presence_only": manifest.get("signing_contract", {}).get("presence_only", {}),
        "keys_printed": False,
        "broad_permissions": False,
        "keystore_in_repo": False,
    }
    print(json.dumps(result, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
