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
    "tests/test_final_release_hardening.py",
    "docs/standards/FINAL_RELEASE_HARDENING_V1_STANDARD.md",
    "docs/release/FINAL_RELEASE_HARDENING_REPORT.md",
    "docs/release/FINAL_RELEASE_HARDENING_REPORT.json",
    "docs/release/RELEASE_NOTES_V1.md",
    "scripts/final_release_hardening.py",
    "tests/test_recursive_grandchild_inheritance.py",
    "docs/standards/RECURSIVE_GRANDCHILD_INHERITANCE_V1_STANDARD.md",
    "docs/RECURSIVE_GRANDCHILD_INHERITANCE.md",
    "scripts/prove_recursive_grandchild_inheritance.py",
    "ai_workflow_os/recursive_inheritance.py",
    "tests/test_apk_pipeline.py",
    "docs/standards/APK_BUILD_SIGN_PIPELINE_V1_STANDARD.md",
    "docs/APK_BUILD_SIGN_PIPELINE.md",
    "scripts/prove_apk_pipeline.py",
    "ai_workflow_os/apk_pipeline.py",
    "tests/test_agent_routed_builder.py",
    "docs/standards/AGENT_ROUTED_BUILDER_V1_STANDARD.md",
    "docs/AGENT_ROUTED_BUILDER.md",
    "scripts/prove_agent_routed_builder.py",
    "ai_workflow_os/agent_builder.py",
    "tests/test_mobile_command_v7.py",
    "docs/standards/MOBILE_COMMAND_SURFACE_V7_STANDARD.md",
    "web/assets/mobile-command-v7.js",
    "web/assets/mobile-command-v7.css",
    "tests/test_editorial_ux_v6.py",
    "docs/standards/EDITORIAL_UX_V6_STANDARD.md",
    "web/assets/page-content-v2.data.json",
    "web/assets/native-app-mode.js",
    "web/assets/editorial-pages.js",
    "web/assets/editorial-ux-v6.css",
    "tests/test_runtime_console_ux_density.py",
    "docs/standards/RUNTIME_CONSOLE_UX_DENSITY_STANDARD.md",
    "web/assets/verbose-pages.data.json",
    "web/assets/ux-density-v5.css",
    "web/assets/runtime-console.js",
    "ai_workflow_os/runtime_console.py",
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
