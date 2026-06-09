from pathlib import Path
from ai_workflow_os.app_pumps import boundary_manifest, pump_manifest, standards_audit, generated_app_preflight, mistake_prevention_manifest, operating_memory_manifest
from ai_workflow_os.registry_spine import build_registry, dispatch

def test_pump_files_write_registries():
    assert boundary_manifest()["ok"] is True
    assert pump_manifest()["ok"] is True
    assert standards_audit()["ok"] is True
    assert generated_app_preflight()["ok"] is True
    assert mistake_prevention_manifest()["ok"] is True
    assert operating_memory_manifest()["ok"] is True
    assert Path("ai_workflow_os/registries/operating_boundary.json").exists()
    assert Path("ai_workflow_os/registries/pumps.json").exists()
    assert Path("ai_workflow_os/registries/standards.json").exists()
    assert Path("ai_workflow_os/registries/generated_app_preflight.json").exists()
    assert Path("ai_workflow_os/registries/mistake_prevention.json").exists()
    assert Path("ai_workflow_os/registries/operating_memory.json").exists()

def test_registry_contains_pump_actions():
    ids = {a["id"] for a in build_registry().manifest()["actions"]}
    assert "os.boundary" in ids
    assert "pump.manifest" in ids
    assert "standards.audit" in ids
    assert "app_factory.preflight" in ids
    assert "mistakes.prevent" in ids
    assert "memory.manifest" in ids

def test_dispatch_pump_action_creates_proof():
    result = dispatch("standards.audit", {}, source="test")
    assert result["ok"] is True
    assert Path(result["proof_path"]).exists()
