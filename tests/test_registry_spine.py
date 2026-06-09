
from pathlib import Path

from ai_workflow_os.registry_spine.spine import build_registry, dispatch, STATE, AUDIT, PROOFS

def test_manifest_has_actions():
    m = build_registry().manifest()
    ids = {a["id"] for a in m["actions"]}
    assert "system.health" in ids
    assert "registry.rebuild" in ids
    assert "verify.python" in ids
    assert "verify.workflow" in ids

def test_health_dispatch_creates_proof():
    result = dispatch("system.health", {}, source="test")
    assert result["ok"] is True
    assert Path(result["proof_path"]).exists()
    assert (STATE / "events.jsonl").exists()
    assert (AUDIT / "audit.jsonl").exists()
    assert PROOFS.exists()

def test_secret_payload_rejected():
    result = dispatch("system.health", {"api_key": "DO_NOT_PRINT"}, source="test")
    assert result["ok"] is False
    assert result["message"] == "payload rejected"
