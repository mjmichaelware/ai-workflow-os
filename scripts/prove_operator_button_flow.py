from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / 'generated_apps'
ARCHIVE_ROOT = Path.home() / 'tmp'

def request_json(path: str, payload: dict | None = None) -> dict:
    url = 'http://127.0.0.1:8765' + path
    if payload is None:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=240) as response:
        return json.loads(response.read().decode('utf-8'))

def app_names() -> set[str]:
    if not GENERATED.exists():
        return set()
    return {item.name for item in GENERATED.iterdir() if item.is_dir()}

def main() -> int:
    before = app_names()
    status = request_json('/api/operator/status')
    export = request_json('/api/phone/export', {})
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    app_name = 'console-button-proof-' + stamp
    prompt = 'Create an app named ' + app_name + ' that proves the console build button works. It must include a browser UI, app.py, README, and smoke test.'
    build = request_json('/api/operator/run', {'prompt': prompt, 'publish': False})
    time.sleep(1)
    after = app_names()
    created = sorted(after - before)
    if not created and build.get('created_apps'):
        created = [app.get('name', 'unknown') for app in build.get('created_apps', [])]
    archive = ARCHIVE_ROOT / ('aiwos_button_flow_proof_' + stamp)
    archive.mkdir(parents=True, exist_ok=True)
    material_files = []
    for name in created:
        app_info = None
        for item in build.get('created_apps', []):
            if item.get('name') == name:
                app_info = item
                break
        source = Path(app_info.get('path')) if app_info and app_info.get('path') else GENERATED / name
        if source.exists():
            for required in ['app.py', 'README.md', 'APP_MANIFEST.json']:
                if (source / required).exists():
                    material_files.append(str(source / required))
            shutil.move(str(source), str(archive / name))
    result = {
        'ok': bool(status.get('ok')) and bool(export.get('ok')) and bool(build.get('ok')) and bool(created) and bool(material_files),
        'status_ok': bool(status.get('ok')),
        'export_ok': bool(export.get('ok')),
        'build_ok': bool(build.get('ok')),
        'created_generated_apps': created,
        'material_files_seen_before_archive': material_files,
        'archive': str(archive),
        'keys_printed': False,
        'button_endpoints_proven': ['/api/operator/status', '/api/phone/export', '/api/operator/run'],
    }
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
