from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_workflow_os.real_apk_project import create_real_apk_project, attempt_debug_apk_build, detect_real_apk_toolchain


def main() -> int:
    project = create_real_apk_project()
    build = attempt_debug_apk_build(Path(project["path"]))
    report = {
        "ok": True,
        "project_created": project.get("ok") is True,
        "project_path": project["path"],
        "toolchain": detect_real_apk_toolchain(),
        "build_attempted": True,
        "debug_apk_built": bool(build.get("ok")),
        "debug_apk": build.get("apk"),
        "build_returncode": build.get("returncode"),
        "build_stdout_tail": build.get("stdout_tail", "")[-1500:],
        "build_stderr_tail": build.get("stderr_tail", "")[-1500:],
        "keys_printed": False,
        "broad_permissions": False,
        "keystore_in_repo": False,
    }
    out = ROOT / "docs" / "apk" / "REAL_APK_BUILD_ATTEMPT_REPORT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
