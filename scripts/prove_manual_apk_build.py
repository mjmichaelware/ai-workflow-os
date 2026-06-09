from __future__ import annotations

from pathlib import Path
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_workflow_os.manual_apk_builder import build_manual_debug_apk


def main() -> int:
    result = build_manual_debug_apk()
    out = ROOT / "docs" / "apk" / "MANUAL_APK_BUILD_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    copied_to = None
    apk = result.get("debug_apk")
    if apk and Path(apk).exists():
        dest_dir = Path.home() / "storage" / "downloads"
        if not dest_dir.exists():
            dest_dir = Path.home() / "tmp"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "AI-Workflow-OS-debug.apk"
        shutil.copy2(apk, dest)
        copied_to = str(dest)

    summary = {
        "ok": result.get("ok") is True,
        "stage": result.get("stage"),
        "debug_apk": apk,
        "copied_to": copied_to,
        "report": str(out),
        "keys_printed": False,
        "broad_permissions": False,
        "keystore_committed": False,
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
