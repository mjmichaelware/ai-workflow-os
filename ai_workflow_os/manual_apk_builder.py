from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import datetime
import json
import os
import secrets
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "exports" / "manual_apk_project"


def tool(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: List[str], cwd: Path | None = None, timeout: int = 240, env: dict | None = None) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=env or os.environ.copy(),
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except Exception as exc:
        return {"ok": False, "returncode": 1, "stdout_tail": "", "stderr_tail": str(exc)}


def detect_manual_apk_toolchain() -> Dict[str, Any]:
    tools = {}
    for name in ["java", "javac", "keytool", "aapt2", "d8", "zipalign", "apksigner"]:
        tools[name] = {"installed": tool(name) is not None, "path": tool(name)}
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT") or str(Path.home() / "android-sdk")
    android_jar = Path(android_home) / "platforms" / "android-36" / "android.jar"
    return {
        "ok": all(item["installed"] for item in tools.values()) and android_jar.exists(),
        "tools": tools,
        "android_home_present": bool(android_home),
        "android_jar": str(android_jar),
        "android_jar_exists": android_jar.exists(),
        "keys_printed": False,
    }


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def create_manual_apk_source(app_name: str = "AI Workflow OS", package_name: str = "com.aiworkflowos.manual") -> Dict[str, Any]:
    out = EXPORT_ROOT / "ai-workflow-os-manual"
    if out.exists():
        shutil.rmtree(out)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    java_dir = out / "src" / "com" / "aiworkflowos" / "manual"
    _write(out / "res" / "values" / "strings.xml", f"""
<resources>
    <string name="app_name">{app_name}</string>
</resources>
""")

    _write(out / "AndroidManifest.xml", f"""
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{package_name}">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application
        android:label="{app_name}"
        android:theme="@android:style/Theme.Material.NoActionBar"
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

    _write(java_dir / "MainActivity.java", """
package com.aiworkflowos.manual;

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
        webView.loadUrl("http://127.0.0.1:8765/?native=manual-apk");
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

    _write(out / "README.md", f"""# {app_name} Termux-Native Manual APK

This APK project bypasses Gradle and uses Termux-native Android tools:

- aapt2
- javac
- d8
- zipalign
- apksigner

The APK loads the local AI Workflow OS operator URL:

`http://127.0.0.1:8765/?native=manual-apk`

No production keystore, password, token, or API key is stored here.
""")

    payload = {
        "ok": True,
        "created_at": now,
        "path": str(out),
        "package_name": package_name,
        "keys_printed": False,
        "broad_permissions": False,
    }
    (out / "MANUAL_APK_PROJECT.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def build_manual_debug_apk() -> Dict[str, Any]:
    project = create_manual_apk_source()
    project_dir = Path(project["path"])
    toolchain = detect_manual_apk_toolchain()
    if not toolchain["ok"]:
        return {
            "ok": False,
            "stage": "toolchain",
            "project": project,
            "toolchain": toolchain,
            "keys_printed": False,
            "broad_permissions": False,
        }

    android_jar = Path(toolchain["android_jar"])
    build = project_dir / "build"
    classes = build / "classes"
    dex = build / "dex"
    build.mkdir(parents=True, exist_ok=True)
    classes.mkdir(parents=True, exist_ok=True)
    dex.mkdir(parents=True, exist_ok=True)

    package_name = "com.aiworkflowos.manual"
    compiled_res = build / "compiled-res"
    gen_java = build / "gen"
    compiled_res.mkdir(parents=True, exist_ok=True)
    gen_java.mkdir(parents=True, exist_ok=True)

    base_apk = build / "base.apk"
    dex_apk = build / "with-classes.apk"
    aligned_apk = build / "aligned.apk"
    signed_apk = build / "AI-Workflow-OS-debug.apk"

    steps: List[Dict[str, Any]] = []

    res_files = [str(p) for p in (project_dir / "res").rglob("*") if p.is_file()]
    if res_files:
        steps.append(run([
            tool("aapt2") or "aapt2",
            "compile",
            "--dir", str(project_dir / "res"),
            "-o", str(compiled_res),
        ], cwd=project_dir))

    flat_files = [str(p) for p in compiled_res.rglob("*.flat")]
    link_cmd = [
        tool("aapt2") or "aapt2",
        "link",
        "-o", str(base_apk),
        "--manifest", str(project_dir / "AndroidManifest.xml"),
        "-I", str(android_jar),
        "--java", str(gen_java),
        "--min-sdk-version", "26",
        "--target-sdk-version", "36",
        "--version-code", "1",
        "--version-name", "1.2.0",
    ] + flat_files
    steps.append(run(link_cmd, cwd=project_dir))

    java_files = [str(p) for p in (project_dir / "src").rglob("*.java")] + [str(p) for p in gen_java.rglob("*.java")]
    steps.append(run([
        tool("javac") or "javac",
        "-source", "8",
        "-target", "8",
        "-classpath", str(android_jar),
        "-d", str(classes),
        *java_files,
    ], cwd=project_dir))

    class_files = [str(p) for p in classes.rglob("*.class")]
    steps.append(run([
        tool("d8") or "d8",
        "--lib", str(android_jar),
        "--min-api", "26",
        "--output", str(dex),
        *class_files,
    ], cwd=project_dir))

    if not all(step["ok"] for step in steps):
        return {
            "ok": False,
            "stage": "compile",
            "project": project,
            "toolchain": toolchain,
            "steps": steps,
            "keys_printed": False,
            "broad_permissions": False,
        }

    shutil.copy2(base_apk, dex_apk)
    with zipfile.ZipFile(dex_apk, "a", compression=zipfile.ZIP_DEFLATED) as apk_zip:
        apk_zip.write(dex / "classes.dex", "classes.dex")

    steps.append(run([
        tool("zipalign") or "zipalign",
        "-f",
        "4",
        str(dex_apk),
        str(aligned_apk),
    ], cwd=project_dir))

    keystore = build / "debug.keystore"
    alias = "aiwosdebug"
    password = "pw_" + secrets.token_urlsafe(24)

    steps.append(run([
        tool("keytool") or "keytool",
        "-genkeypair",
        "-v",
        "-keystore", str(keystore),
        "-storepass", password,
        "-keypass", password,
        "-alias", alias,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "30",
        "-dname", "CN=AI Workflow OS Debug,O=Local,C=US",
        "-noprompt",
    ], cwd=project_dir))

    steps.append(run([
        tool("apksigner") or "apksigner",
        "sign",
        "--ks", str(keystore),
        "--ks-key-alias", alias,
        "--ks-pass", "pass:" + password,
        "--key-pass", "pass:" + password,
        "--out", str(signed_apk),
        str(aligned_apk),
    ], cwd=project_dir))

    steps.append(run([
        tool("apksigner") or "apksigner",
        "verify",
        "--verbose",
        str(signed_apk),
    ], cwd=project_dir))

    ok = signed_apk.exists() and all(step["ok"] for step in steps)
    return {
        "ok": ok,
        "stage": "signed" if ok else "sign_or_verify",
        "project": project,
        "toolchain": toolchain,
        "steps": steps,
        "debug_apk": str(signed_apk) if signed_apk.exists() else None,
        "keys_printed": False,
        "broad_permissions": False,
        "keystore_committed": False,
    }
