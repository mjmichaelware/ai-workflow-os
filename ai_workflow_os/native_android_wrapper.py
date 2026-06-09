
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import datetime
import json
import re

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "exports" / "android_wrappers"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "ai-workflow-os").lower()).strip("-")
    return value[:72] or "ai-workflow-os"


def package_name(value: str) -> str:
    slug = slugify(value).replace("-", "")
    if not slug or not slug[0].isalpha():
        slug = "app" + slug
    return "com.aiworkflowos." + slug[:48]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def export_native_android_wrapper(app_name: str = "AI Workflow OS", start_url: str = "http://127.0.0.1:8765/") -> Dict[str, Any]:
    slug = slugify(app_name)
    out = EXPORT_ROOT / slug
    pkg = package_name(app_name)
    kt_dir = out / "app" / "src" / "main" / "java" / "com" / "aiworkflowos" / slug.replace("-", "")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    write_json(out / "WRAPPER_MANIFEST.json", {
        "ok": True,
        "name": app_name,
        "slug": slug,
        "package": pkg,
        "created_at": now,
        "start_url": start_url,
        "type": "native-android-wrapper-scaffold",
        "permissions": [],
        "broad_permissions": False,
        "network_scope": "local-first",
        "keys_printed": False,
        "build_stage": "scaffold-only",
    })

    write_text(out / "README.md", f"""# {app_name} Android Wrapper Scaffold

This export creates the file layout for a future signed Android wrapper.

It is intentionally scaffold-only:
- no broad permissions
- no embedded secrets
- no forced install
- no signing keys
- local-first entrypoint: {start_url}

A later explicit build/sign stage can turn this scaffold into an APK project.
""")

    write_text(out / "settings.gradle", f"""pluginManagement {{ repositories {{ google(); mavenCentral(); gradlePluginPortal() }} }}
dependencyResolutionManagement {{ repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories {{ google(); mavenCentral() }} }}
rootProject.name = "{slug}"
include ":app"
""")

    write_text(out / "build.gradle", """plugins {
    id "com.android.application" version "8.5.2" apply false
}
""")

    write_text(out / "app" / "build.gradle", f"""plugins {{
    id "com.android.application"
}}

android {{
    namespace "{pkg}"
    compileSdk 35

    defaultConfig {{
        applicationId "{pkg}"
        minSdk 26
        targetSdk 35
        versionCode 1
        versionName "0.1.0"
    }}
}}
""")

    write_text(out / "app" / "src" / "main" / "AndroidManifest.xml", f"""<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="false"
        android:label="{app_name}"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    write_text(kt_dir / "MainActivity.kt", f"""package {pkg}

import android.app.Activity
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        val webView = WebView(this)
        webView.webViewClient = WebViewClient()
        webView.settings.javaScriptEnabled = true
        webView.loadUrl("{start_url}")
        setContentView(webView)
    }}
}}
""")

    write_text(out / "app" / "src" / "main" / "res" / "values" / "styles.xml", """<resources>
    <style name="AppTheme" parent="android:style/Theme.Material.NoActionBar">
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:fontFamily">sans</item>
        <item name="android:colorAccent">#7bdcff</item>
    </style>
</resources>
""")

    write_text(out / "app" / "src" / "main" / "res" / "drawable" / "launcher_icon.xml", """<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#07111f" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#7bdcff" android:pathData="M20,72 L54,16 L88,72 L68,72 L54,48 L40,72 Z"/>
    <path android:fillColor="#74f0aa" android:pathData="M54,82m-8,0a8,8 0,1 0,16 0a8,8 0,1 0,-16 0"/>
</vector>
""")

    write_json(out / "proof" / "native_wrapper_proof.json", {
        "ok": True,
        "created_at": now,
        "files": [
            "WRAPPER_MANIFEST.json",
            "settings.gradle",
            "build.gradle",
            "app/build.gradle",
            "app/src/main/AndroidManifest.xml",
            "app/src/main/java/.../MainActivity.kt",
            "app/src/main/res/values/styles.xml",
            "app/src/main/res/drawable/launcher_icon.xml",
        ],
        "keys_printed": False,
        "broad_permissions": False,
    })

    return {
        "ok": True,
        "path": str(out),
        "package": pkg,
        "start_url": start_url,
        "keys_printed": False,
        "broad_permissions": False,
    }


if __name__ == "__main__":
    print(json.dumps(export_native_android_wrapper(), indent=2))
