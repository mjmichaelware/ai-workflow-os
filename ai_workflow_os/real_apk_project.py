from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import datetime
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "exports" / "real_apk_project"


def tool_path(name: str) -> str | None:
    return shutil.which(name)


def detect_real_apk_toolchain() -> Dict[str, Any]:
    tools = {}
    for name in ["java", "javac", "gradle", "sdkmanager", "adb", "apksigner", "zipalign", "aapt2", "d8", "keytool"]:
        tools[name] = {"installed": tool_path(name) is not None, "path": tool_path(name)}
    return {
        "ok": True,
        "tools": tools,
        "android_home_present": bool(os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")),
        "keys_printed": False,
    }


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def create_real_apk_project(app_name: str = "AI Workflow OS", package_name: str = "com.aiworkflowos.mobile") -> Dict[str, Any]:
    out = EXPORT_ROOT / "ai-workflow-os-mobile"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    _write(out / "settings.gradle", """
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "AIWorkflowOSMobile"
include ":app"
""")

    _write(out / "build.gradle", """
plugins {
    id "com.android.application" version "8.7.3" apply false
}
""")

    _write(out / "gradle.properties", """
android.useAndroidX=true
android.nonTransitiveRClass=true
org.gradle.jvmargs=-Xmx1536m -Dfile.encoding=UTF-8
""")

    _write(out / "app" / "build.gradle", f"""
plugins {{
    id "com.android.application"
}}

android {{
    namespace "{package_name}"
    compileSdk 36

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 26
        targetSdk 36
        versionCode 1
        versionName "1.1.0"
    }}
}}
""")

    _write(out / "app" / "src" / "main" / "AndroidManifest.xml", f"""
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application
        android:theme="@style/AppTheme"
        android:label="{app_name}"
        android:usesCleartextTraffic="true"
        android:allowBackup="false"
        android:supportsRtl="true">
        <activity
            android:name=".MainActivity"
            android:screenOrientation="portrait"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    _write(out / "app" / "src" / "main" / "res" / "values" / "styles.xml", """
<resources>
    <style name="AppTheme" parent="android:style/Theme.Material.NoActionBar">
        <item name="android:windowFullscreen">true</item>
        <item name="android:fontFamily">sans</item>
        <item name="android:colorAccent">#8b5cf6</item>
        <item name="android:navigationBarColor">#050713</item>
        <item name="android:statusBarColor">#050713</item>
    </style>
</resources>
""")

    _write(out / "app" / "src" / "main" / "java" / "com" / "aiworkflowos" / "mobile" / "MainActivity.java", """
package com.aiworkflowos.mobile;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);

        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("http://127.0.0.1:8765/?native=apk");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
            return;
        }
        super.onBackPressed();
    }
}
""")

    _write(out / "README.md", f"""# {app_name} Real APK Project

This is a generated Gradle Android WebView project for AI Workflow OS.

It points to the local device operator URL:

`http://127.0.0.1:8765/?native=apk`

No signing keys, passwords, API tokens, or keystores are stored here.
""")

    payload = {
        "ok": True,
        "created_at": now,
        "path": str(out),
        "app_name": app_name,
        "package_name": package_name,
        "toolchain": detect_real_apk_toolchain(),
        "keys_printed": False,
        "broad_permissions": False,
        "keystore_in_repo": False,
    }
    (out / "REAL_APK_PROJECT.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def attempt_debug_apk_build(project_dir: Path) -> Dict[str, Any]:
    project_dir = Path(project_dir)
    if tool_path("gradle") is None:
        return {"ok": False, "reason": "gradle missing", "keys_printed": False}
    result = subprocess.run(
        ["gradle", ":app:assembleDebug", "--stacktrace"],
        cwd=project_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=900,
        env=os.environ.copy(),
    )
    apk = project_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    return {
        "ok": result.returncode == 0 and apk.exists(),
        "returncode": result.returncode,
        "apk": str(apk) if apk.exists() else None,
        "stdout_tail": result.stdout[-6000:],
        "stderr_tail": result.stderr[-6000:],
        "keys_printed": False,
    }
