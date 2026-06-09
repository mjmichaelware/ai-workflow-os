from ai_workflow_os.operator_console import operator_manifest, operator_status

def test_operator_manifest():
    data = operator_manifest()
    assert data["ok"] is True
    assert data["raw_shell"] is False
    assert "/api/operator/run" in data["endpoints"]

def test_operator_status():
    data = operator_status()
    assert data["ok"] is True
    assert "inventory" in data
    assert data["inventory"]["keys_are_not_stored_or_printed"] is True

