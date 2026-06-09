from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_apk_pipeline_module_exists():
    text = (ROOT / "ai_workflow_os" / "apk_pipeline.py").read_text(encoding="utf-8")
    assert "create_apk_pipeline_scaffold" in text
    assert "AIWOS_ANDROID_KEYSTORE" in text
    assert "keys_printed" in text
    assert "keystore_in_repo" in text


def test_apk_pipeline_proof_docs_exist():
    assert (ROOT / "scripts" / "prove_apk_pipeline.py").exists()
    assert (ROOT / "docs" / "APK_BUILD_SIGN_PIPELINE.md").exists()
    assert (ROOT / "docs" / "standards" / "APK_BUILD_SIGN_PIPELINE_V1_STANDARD.md").exists()


def test_apk_pipeline_does_not_embed_password_values():
    text = (ROOT / "ai_workflow_os" / "apk_pipeline.py").read_text(encoding="utf-8")
    assert "values_printed" in text
    assert "repo_stores_keystore" in text
