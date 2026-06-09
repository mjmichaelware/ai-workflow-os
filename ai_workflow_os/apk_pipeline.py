from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import datetime
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_ROOT = ROOT / "exports" / "apk_pipeline"


def which(name: str) -> str | None:
    return shutil.which(name)


def detect_android_toolchain() -> Dict[str, Any]:
    tools = {}
    for name in ["java", "javac", "gradle", "keytool", "apksigner", "zipalign", "sdkmanager"]:
        tools[name] = {"installed": which(name) is not None, "path": which(name)}
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    return {
        "ok": True,
        "tools": tools,
        "android_home_present": bool(android_home),
        "android_home_path_present_only": bool(android_home),
        "keys_printed": False,
    }


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def apk_signing_env_contract() -> Dict[str, Any]:
    names = [
        "AIWOS_ANDROID_KEYSTORE",
        "AIWOS_ANDROID_KEY_ALIAS",
        "AIWOS_ANDROID_KEYSTORE_PASSWORD",
        "AIWOS_ANDROID_KEY_PASSWORD",
    ]
    return {
        "ok": True,
        "required_env": names,
        "presence_only": {name: bool(os.environ.get(name)) for name in names},
        "values_printed": False,
        "keys_printed": False,
        "repo_stores_keystore": False,
    }


def create_apk_pipeline_scaffold(app_name: str = "AI Workflow OS") -> Dict[str, Any]:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in app_name).strip("-") or "ai-workflow-os"
    out = PIPELINE_ROOT / slug
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    _write(out / "README.md", f"""# APK Pipeline Scaffold: {app_name}

This directory is a generated scaffold for building and signing an Android wrapper.

It intentionally does not contain:
- signing keys
- keystores
- passwords
- broad permissions
- embedded API tokens

Signing material must be supplied from environment variables outside the repository.
""")

    _write(out / "build_apk.sh", """#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

if ! command -v gradle >/dev/null 2>&1; then
  echo "gradle is required to build the APK"
  exit 2
fi

gradle :app:assembleRelease
""")

    _write(out / "sign_apk.sh", """#!/usr/bin/env bash
set -euo pipefail

: "${AIWOS_ANDROID_KEYSTORE:?missing keystore path}"
: "${AIWOS_ANDROID_KEY_ALIAS:?missing key alias}"
: "${AIWOS_ANDROID_KEYSTORE_PASSWORD:?missing keystore password}"
: "${AIWOS_ANDROID_KEY_PASSWORD:?missing key password}"

UNSIGNED_APK="${1:?path to unsigned APK required}"
SIGNED_APK="${2:?path to signed APK required}"

if ! command -v apksigner >/dev/null 2>&1; then
  echo "apksigner is required to sign the APK"
  exit 2
fi

apksigner sign \\
  --ks "$AIWOS_ANDROID_KEYSTORE" \\
  --ks-key-alias "$AIWOS_ANDROID_KEY_ALIAS" \\
  --ks-pass "env:AIWOS_ANDROID_KEYSTORE_PASSWORD" \\
  --key-pass "env:AIWOS_ANDROID_KEY_PASSWORD" \\
  --out "$SIGNED_APK" \\
  "$UNSIGNED_APK"
""")

    _write(out / "verify_apk.sh", """#!/usr/bin/env bash
set -euo pipefail

APK="${1:?path to signed APK required}"

if ! command -v apksigner >/dev/null 2>&1; then
  echo "apksigner is required to verify the APK"
  exit 2
fi

apksigner verify --verbose "$APK"
""")

    for rel in ["build_apk.sh", "sign_apk.sh", "verify_apk.sh"]:
        (out / rel).chmod(0o755)

    payload = {
        "ok": True,
        "created_at": now,
        "path": str(out),
        "app_name": app_name,
        "slug": slug,
        "toolchain": detect_android_toolchain(),
        "signing_contract": apk_signing_env_contract(),
        "scripts": ["build_apk.sh", "sign_apk.sh", "verify_apk.sh"],
        "keys_printed": False,
        "broad_permissions": False,
        "keystore_in_repo": False,
        "stage": "scaffold",
    }
    (out / "APK_PIPELINE_MANIFEST.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(create_apk_pipeline_scaffold(), indent=2))
