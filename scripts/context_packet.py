from __future__ import annotations

from pathlib import Path
import base64
import datetime
import gzip
import hashlib
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "tests/test_final_proof_dashboard.py",
    "docs/standards/FINAL_PROOF_DASHBOARD_STANDARD.md",
    "docs/proof/FINAL_PERFECTION_REPORT.md",
    "docs/proof/FINAL_PERFECTION_REPORT.json",
    "scripts/final_perfection_report.py",
    "web/assets/final-proof-dashboard.meta.json",
    "web/assets/final-proof-dashboard.data.json",
    "web/assets/final-proof-dashboard.js",
    "web/assets/visual-max-v4.css",
    ".github/dependabot.yml",
    ".github/workflows/ci.yml",
    "tests/test_capability_matrix.py",
    "docs/standards/CAPABILITY_MATRIX_STANDARD.md",
    "docs/capabilities/TOOL_AGENT_CAPABILITY_MATRIX.md",
    "docs/capabilities/TOOL_AGENT_CAPABILITY_MATRIX.json",
    "scripts/prove_capability_matrix.py",
    "ai_workflow_os/capability_matrix.py",
    "tests/test_native_android_wrapper.py",
    "docs/standards/NATIVE_ANDROID_WRAPPER_STANDARD.md",
    "docs/NATIVE_ANDROID_WRAPPER.md",
    "scripts/prove_native_android_wrapper.py",
    "ai_workflow_os/native_android_wrapper.py",
    "tests/test_generated_app_shell.py",
    "docs/standards/GENERATED_APP_SHELL_INHERITANCE_V2_STANDARD.md",
    "docs/GENERATED_APP_PACKAGING.md",
    "scripts/prove_generated_app_shell.py",
    "ai_workflow_os/generated_app_shell.py",
    "docs/standards/VISUAL_SYSTEM_V3_STANDARD.md",
    "web/assets/visual-system-v3.meta.json",
    "web/assets/endpoint-graph.data.json",
    "web/assets/endpoint-graph.js",
    "web/assets/visual-system-v3.css",
    "README.md",
    "AGENTS.md",
    "GEMINI.md",
    "CLAUDE.md",
    "CODEX.md",
    "SECURITY.md",
    "PRIVACY.md",
    "LICENSE",
    "ai_workflow_os/operator_console.py",
    "ai_workflow_os/server.py",
    "web/index.html",
    "web/assets/console.css",
    "web/assets/console.js",
    "web/assets/console.meta.json",
    "scripts/prove_operator_button_flow.py",
    'docs/standards/PUBLIC_SURFACE_HYGIENE_STANDARD.md',
    'docs/research/DEVELOPER_DIRECTION_2026.md',
    'scripts/verify_public_surface.py',
    'scripts/research_developer_direction.py',
    'scripts/prove_recursive_app_factory.py',
    "tests/test_console_ui.py",
    "docs/FRONTEND_ARCHITECTURE.md",
    "docs/standards/UI_PACKET_ARCHITECTURE_STANDARD.md",
]

def build_packet() -> dict:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for rel in FILES:
            path = ROOT / rel
            if path.exists():
                tar.add(path, arcname=rel)
    gz = gzip.compress(raw.getvalue(), compresslevel=9)
    encoded = base64.b64encode(gz).decode("ascii")
    return {
        "ok": True,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "format": "tar.gz.base64",
        "sha256": hashlib.sha256(gz).hexdigest(),
        "bytes": len(gz),
        "files": [rel for rel in FILES if (ROOT / rel).exists()],
        "payload": encoded,
    }

def main() -> int:
    out = ROOT / "docs" / "context" / "AI_WORKFLOW_OS_CONTEXT_PACKET.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    packet = build_packet()
    out.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(json.dumps({key: packet[key] for key in ["ok", "created_at", "format", "sha256", "bytes", "files"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
