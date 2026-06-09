
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_final_visual_assets_exist_and_are_wired():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "web" / "assets" / "console.js").read_text(encoding="utf-8")
    assert "/assets/visual-max-v4.css" in html
    assert "/assets/final-proof-dashboard.js" in html
    assert "id:\"proof\"" in js

def test_final_proof_dashboard_data():
    data = json.loads((ROOT / "web" / "assets" / "final-proof-dashboard.data.json").read_text(encoding="utf-8"))
    assert data["ok"] is True
    assert len(data["proofs"]) >= 8
    assert any(item["id"] == "factory" for item in data["proofs"])
    assert any(item["id"] == "android" for item in data["proofs"])

def test_final_ci_and_report_scripts_exist():
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()
    assert (ROOT / ".github" / "dependabot.yml").exists()
    assert (ROOT / "scripts" / "final_perfection_report.py").exists()
    assert (ROOT / "docs" / "standards" / "FINAL_PROOF_DASHBOARD_STANDARD.md").exists()
