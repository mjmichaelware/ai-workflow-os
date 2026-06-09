from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import base64
import datetime
import gzip
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
GENERATED_ROOT = ROOT / "generated_apps"

ICON_SVG = """<svg xmlns=\\"http://www.w3.org/2000/svg\\" viewBox=\\"0 0 128 128\\"><defs><linearGradient id=\\"g\\" x1=\\"0\\" x2=\\"1\\" y1=\\"0\\" y2=\\"1\\"><stop stop-color=\\"#7bdcff\\"/><stop offset=\\"1\\" stop-color=\\"#c8a5ff\\"/></linearGradient></defs><rect width=\\"128\\" height=\\"128\\" rx=\\"30\\" fill=\\"#07111f\\"/><path d=\\"M24 82 64 18l40 64H79l-15-25-15 25z\\" fill=\\"url(#g)\\"/><circle cx=\\"64\\" cy=\\"92\\" r=\\"10\\" fill=\\"#74f0aa\\"/></svg>"""

def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")[:72] or "generated-app"

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\\n", encoding="utf-8")

def _json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")

def ensure_generated_app_shell(app_dir: Path, title: str | None = None) -> Dict[str, Any]:
    app_dir = Path(app_dir)
    app_dir.mkdir(parents=True, exist_ok=True)
    name = app_dir.name
    title = title or name.replace("-", " ").title()
    web = app_dir / "web"
    assets = web / "assets"
    tests = app_dir / "tests"
    android = app_dir / "android_wrapper"
    proof = app_dir / "proof"
    for item in [web, assets, tests, android, proof]:
        item.mkdir(parents=True, exist_ok=True)

    _write(assets / "icon.svg", ICON_SVG)
    _write(assets / "app.css", """body{margin:0;background:radial-gradient(circle at 20% 20%,rgba(123,220,255,.16),transparent 30%),linear-gradient(180deg,#07111f,#050b14);color:#edf6ff;font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}main{max-width:920px;margin:auto;padding:28px}.shell{border:1px solid rgba(123,220,255,.28);border-radius:28px;padding:22px;background:rgba(12,30,51,.72);box-shadow:0 24px 80px rgba(0,0,0,.35);backdrop-filter:blur(16px)}h1{font-size:clamp(2rem,8vw,4.2rem);line-height:.95;margin:0;background:linear-gradient(90deg,#edf6ff,#7bdcff,#c8a5ff);-webkit-background-clip:text;background-clip:text;color:transparent}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:20px}.card{border:1px solid rgba(123,220,255,.18);border-radius:20px;padding:14px;background:rgba(7,17,31,.74);transition:transform .18s ease,border-color .18s ease}.card:hover{transform:translateY(-3px);border-color:#7bdcff}button{border:0;border-radius:999px;padding:12px 16px;font-weight:900;background:#7bdcff;color:#06101d}pre{white-space:pre-wrap;border:1px solid rgba(123,220,255,.18);border-radius:18px;padding:12px;background:#050b14;overflow:auto}@media(prefers-reduced-motion:reduce){.card{transition:none}}""")
    _write(web / "index.html", f"""<!doctype html>
<html lang=\\"en\\">
<head>
  <meta charset=\\"utf-8\\">
  <meta name=\\"viewport\\" content=\\"width=device-width,initial-scale=1\\">
  <title>{title}</title>
  <link rel=\\"manifest\\" href=\\"./manifest.webmanifest\\">
  <link rel=\\"stylesheet\\" href=\\"./assets/app.css\\">
</head>
<body>
<main>
  <section class=\\"shell\\">
    <img src=\\"./assets/icon.svg\\" alt=\\"\\" width=\\"72\\" height=\\"72\\">
    <h1>{title}</h1>
    <p>This app inherits the AI Workflow OS app shell: manifest, service worker, proof packet, icon, Android wrapper scaffold, and child-builder contract.</p>
    <button id=\\"install-app\\">Install</button>
    <div class=\\"grid\\">
      <article class=\\"card\\"><b>Local proof</b><p>Material files and manifest are present.</p></article>
      <article class=\\"card\\"><b>Child builder</b><p>builder.py can generate a child app.</p></article>
      <article class=\\"card\\"><b>Package</b><p>Compressed tar context can be exported.</p></article>
    </div>
    <pre id=\\"status\\">Ready.</pre>
  </section>
</main>
<script src=\\"./assets/app.js\\"></script>
</body>
</html>""")
    _write(assets / "app.js", """let installPrompt=null;window.addEventListener("beforeinstallprompt",event=>{event.preventDefault();installPrompt=event;});document.getElementById("install-app").onclick=async()=>{const status=document.getElementById("status");if(installPrompt){installPrompt.prompt();await installPrompt.userChoice.catch(()=>{});installPrompt=null;status.textContent="Install prompt completed or dismissed.";return;}status.textContent="Install fallback: use browser menu and choose Install app or Add to Home screen.";};if("serviceWorker" in navigator)window.addEventListener("load",()=>navigator.serviceWorker.register("./sw.js").catch(()=>{}));""")
    _write(web / "sw.js", """self.addEventListener("install",event=>self.skipWaiting());self.addEventListener("activate",event=>self.clients.claim());self.addEventListener("fetch",event=>{});""")
    _json(web / "manifest.webmanifest", {
        "name": title,
        "short_name": title[:24],
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#07111f",
        "theme_color": "#07111f",
        "icons": [{"src": "./assets/icon.svg", "sizes": "128x128", "type": "image/svg+xml"}],
    })

    if not (app_dir / "builder.py").exists():
        _write(app_dir / "builder.py", """from __future__ import annotations

from pathlib import Path
import datetime
import json
import re
import sys

ROOT = Path(__file__).resolve().parent

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "child-app").lower()).strip("-")
    return value[:64] or "child-app"

def build_child_app(name: str) -> dict:
    slug = slugify(name)
    target = ROOT / "children" / slug
    target.mkdir(parents=True, exist_ok=True)
    title = slug.replace("-", " ").title()
    (target / "README.md").write_text("# " + title + "\\n\\nBuilt by a generated app shell.\\n", encoding="utf-8")
    (target / "app.py").write_text("APP_NAME = " + json.dumps(title) + "\\n\\ndef health():\\n    return {\\"ok\\": True, \\"app\\": APP_NAME}\\n", encoding="utf-8")
    manifest = {"ok": True, "name": slug, "built_by": "generated-app-shell", "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (target / "APP_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(target), "manifest": manifest}

def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else "child-app"
    print(json.dumps(build_child_app(name), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
""")

    _write(tests / "test_app_shell.py", """from pathlib import Path

def test_app_shell_files_exist():
    root = Path(__file__).resolve().parents[1]
    for rel in [
        "web/index.html",
        "web/manifest.webmanifest",
        "web/sw.js",
        "web/assets/app.css",
        "web/assets/app.js",
        "web/assets/icon.svg",
        "builder.py",
        "APP_MANIFEST.json",
        "android_wrapper/README.md",
        "proof/app_shell_proof.json",
    ]:
        assert (root / rel).exists()
""")

    android_manifest = {
        "ok": True,
        "type": "android-wrapper-scaffold",
        "label": title,
        "package_hint": "com.aiworkflowos." + _safe_name(name).replace("-", ""),
        "local_entrypoint": "web/index.html",
        "launcher_icon": "web/assets/icon.svg",
        "note": "Scaffold only. Native APK build/signing is a later explicit stage.",
    }
    _json(android / "android_wrapper.json", android_manifest)
    _write(android / "README.md", f"""# Android Wrapper Scaffold

This folder is an APK-ready planning scaffold for {title}.

It does not request broad permissions. It declares the app label, icon, and local web entrypoint for a later native wrapper build/sign stage.
""")

    proof_payload = {
        "ok": True,
        "name": name,
        "title": title,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "inherited_shell": True,
        "installable_pwa": True,
        "android_wrapper_scaffold": True,
        "can_build_child_apps": True,
        "keys_printed": False,
        "raw_shell": False,
    }
    _json(proof / "app_shell_proof.json", proof_payload)

    manifest_path = app_dir / "APP_MANIFEST.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    manifest.update({
        "ok": True,
        "name": name,
        "title": title,
        "inherited_shell": True,
        "installable_pwa": True,
        "android_wrapper_scaffold": True,
        "can_build_child_apps": True,
        "shell_files": [
            "web/index.html",
            "web/manifest.webmanifest",
            "web/sw.js",
            "web/assets/app.css",
            "web/assets/app.js",
            "web/assets/icon.svg",
            "builder.py",
            "android_wrapper/android_wrapper.json",
            "proof/app_shell_proof.json",
        ],
    })
    _json(manifest_path, manifest)

    return proof_payload

def build_shell_packet(app_dir: Path) -> Dict[str, Any]:
    app_dir = Path(app_dir)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for rel in ["README.md", "APP_MANIFEST.json", "builder.py", "web", "android_wrapper", "proof"]:
            path = app_dir / rel
            if path.exists():
                tar.add(path, arcname=rel)
    gz = gzip.compress(raw.getvalue(), compresslevel=9)
    payload = {
        "ok": True,
        "format": "tar.gz.base64",
        "bytes": len(gz),
        "payload": base64.b64encode(gz).decode("ascii"),
    }
    _json(app_dir / "proof" / "app_shell_packet.json", payload)
    return payload
