
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_native_wrapper_module_exists():
    text = (ROOT / "ai_workflow_os" / "native_android_wrapper.py").read_text(encoding="utf-8")
    assert "export_native_android_wrapper" in text
    assert "broad_permissions" in text
    assert "keys_printed" in text


def test_native_wrapper_proof_script_exists():
    assert (ROOT / "scripts" / "prove_native_android_wrapper.py").exists()
    assert (ROOT / "docs" / "NATIVE_ANDROID_WRAPPER.md").exists()
    assert (ROOT / "docs" / "standards" / "NATIVE_ANDROID_WRAPPER_STANDARD.md").exists()
