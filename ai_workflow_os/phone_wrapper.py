from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import json
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / 'phone_exports'
DOWNLOADS = Path.home() / 'storage' / 'downloads'

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + chr(10), encoding='utf-8')

def run(cmd: List[str], timeout: int = 120) -> Dict[str, Any]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, shell=False)
    return {'cmd': cmd, 'returncode': p.returncode, 'ok': p.returncode == 0, 'stdout': p.stdout[-8000:], 'stderr': p.stderr[-8000:]}

def phone_manifest() -> Dict[str, Any]:
    data = {
        'ok': True,
        'name': 'AI Workflow OS Phone Wrapper',
        'created_at': now(),
        'local_url': 'http://127.0.0.1:8765',
        'launcher_script': 'bin/open-ai-workflow-os-phone',
        'termux_command': 'bin/open-ai-workflow-os-phone',
        'safe_boundary': 'Browser UI talks to local Termux server through allowlisted endpoints only',
        'command_1': 'Prompt Bridge API',
        'command_2': 'Approval-gated Self Build Executor',
        'command_3': 'Phone Wrapper Export Launcher',
        'endpoints': ['/api/prompts/manifest', '/api/self-build/manifest', '/api/terminal/commands', '/api/actions', '/api/phone/manifest', '/api/phone/export'],
        'can_create_apps_from_phone': True,
        'raw_shell': False,
        'uses_secrets': False,
    }
    write_json(ROOT / 'ai_workflow_os' / 'registries' / 'phone_wrapper.json', data)
    return data

def create_launcher() -> Dict[str, Any]:
    path = ROOT / 'bin' / 'open-ai-workflow-os-phone'
    lines = [
        '#!/data/data/com.termux/files/usr/bin/bash',
        'set -euo pipefail',
        'cd $HOME/Workspaces/AI_Workflow_OS/ai-workflow-os',
        'mkdir -p $HOME/tmp',
        'if curl -fsS http://127.0.0.1:8765/api/phone/status >/dev/null 2>&1; then URL=http://127.0.0.1:8765/?t=$(date +%s); echo OPEN: $URL; if command -v termux-open-url >/dev/null 2>&1; then termux-open-url $URL; fi; exit 0; fi',
        'nohup bin/ai-workflow-os serve --host 127.0.0.1 --port 8765 > $HOME/tmp/ai_workflow_os_dashboard.log 2>&1 &',
        'echo $! > $HOME/tmp/ai_workflow_os_dashboard.pid',
        'sleep 2',
        'URL=http://127.0.0.1:8765/?t=$(date +%s)',
        'echo OPEN: $URL',
        'if command -v termux-open-url >/dev/null 2>&1; then termux-open-url $URL; fi',
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(chr(10).join(lines) + chr(10), encoding='utf-8')
    path.chmod(0o755)
    return {'ok': True, 'path': str(path.relative_to(ROOT)), 'command': str(path)}

def export_phone_bundle() -> Dict[str, Any]:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    manifest = phone_manifest()
    create_launcher()
    bundle = EXPORT_DIR / 'AI_WORKFLOW_OS_PHONE_WRAPPER.zip'
    if bundle.exists():
        bundle.unlink()
    include_roots = ['ai_workflow_os', 'web', 'bin', 'scripts', 'docs', 'tests', 'generated_apps']
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
        for root_name in include_roots:
            base = ROOT / root_name
            if not base.exists():
                continue
            for path in base.rglob('*'):
                if not path.is_file():
                    continue
                rel = path.relative_to(ROOT)
                parts = set(rel.parts)
                if '__pycache__' in parts or '.git' in parts:
                    continue
                if str(rel).endswith('.sqlite3') or str(rel).endswith('.pyc'):
                    continue
                z.write(path, rel.as_posix())
        z.writestr('PHONE_WRAPPER_MANIFEST.json', json.dumps(manifest, indent=2, sort_keys=True))
    target = DOWNLOADS / bundle.name
    shutil.copy2(bundle, target)
    if shutil.which('termux-media-scan'):
        run(['termux-media-scan', str(target)], timeout=30)
    return {'ok': True, 'bundle': str(bundle), 'downloads_copy': str(target), 'size_bytes': target.stat().st_size, 'manifest': manifest}

def phone_status() -> Dict[str, Any]:
    return {'ok': True, 'manifest': phone_manifest(), 'launcher': create_launcher(), 'downloads_exists': DOWNLOADS.exists(), 'local_url': 'http://127.0.0.1:8765'}
