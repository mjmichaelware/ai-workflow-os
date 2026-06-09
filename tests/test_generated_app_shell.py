from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_generated_app_shell_module_exists():
    text = (ROOT / "ai_workflow_os" / "generated_app_shell.py").read_text(encoding="utf-8")
    assert "ensure_generated_app_shell" in text
    assert "build_shell_packet" in text
    assert "android_wrapper" in text
    assert "manifest.webmanifest" in text

def test_operator_uses_generated_app_shell():
    text = (ROOT / "ai_workflow_os" / "operator_console.py").read_text(encoding="utf-8")
    assert "ensure_generated_app_shell" in text
    assert "build_shell_packet" in text

def test_generated_app_shell_standard_exists():
    assert (ROOT / "docs" / "standards" / "GENERATED_APP_SHELL_INHERITANCE_V2_STANDARD.md").exists()
    assert (ROOT / "scripts" / "prove_generated_app_shell.py").exists()
