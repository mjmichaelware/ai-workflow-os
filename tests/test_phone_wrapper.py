from pathlib import Path
from ai_workflow_os.phone_wrapper import phone_manifest, create_launcher, export_phone_bundle, phone_status

def test_phone_manifest():
    data = phone_manifest()
    assert data["ok"] is True
    assert data["raw_shell"] is False
    assert "/api/phone/manifest" in data["endpoints"]

def test_launcher_created():
    data = create_launcher()
    assert data["ok"] is True
    assert Path(data["path"]).exists()

def test_phone_status():
    data = phone_status()
    assert data["ok"] is True

def test_export_bundle_created():
    data = export_phone_bundle()
    assert data["ok"] is True
    assert Path(data["bundle"]).exists()
