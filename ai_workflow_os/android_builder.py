from __future__ import annotations

from pathlib import Path
import re
import shutil
import time

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "generated-android-app"

def android_status() -> dict:
    java = shutil.which("java")
    gradle = shutil.which("gradle")
    return {
        "java": bool(java),
        "gradle": bool(gradle),
        "can_create_native_build_target": True,
        "can_build_apk_here": bool(java and gradle),
        "truth": "APK or AAB build requires Android Gradle tooling. This app reports capability instead of pretending."
    }

def create_native_android_target(repo_root: Path, app_name: str, prompt: str) -> dict:
    name = slugify(app_name)
    out = repo_root.resolve() / "android_targets" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "README.md").write_text("# Android Native Build Target: " + name + "\n\nPrompt:\n\n" + prompt + "\n\nThis is a native Android build target folder. APK/AAB build requires Android Gradle tooling.\n")
    (out / "AI_WORKFLOW_OS_ANDROID_TARGET.json").write_text("{\n  \"name\": " + repr(name).replace(chr(39), chr(34)) + ",\n  \"created_by\": \"AI Workflow OS\"\n}\n")
    return {"ok": True, "name": name, "path": str(out), "status": android_status(), "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
