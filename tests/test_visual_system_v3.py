
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_visual_system_v3_assets_exist():
    for rel in [
        "web/assets/visual-system-v3.css",
        "web/assets/endpoint-graph.js",
        "web/assets/endpoint-graph.data.json",
        "web/assets/visual-system-v3.meta.json",
        "docs/standards/VISUAL_SYSTEM_V3_STANDARD.md",
    ]:
        assert (ROOT / rel).exists()

def test_visual_system_v3_is_wired_to_shell():
    html = read("web/index.html")
    js = read("web/assets/console.js") + read("web/assets/endpoint-graph.js")
    css = read("web/assets/visual-system-v3.css")
    assert "/assets/visual-system-v3.css" in html
    assert "/assets/endpoint-graph.js" in html
    assert "id:\"graph\"" in js
    assert "AIWOS_ENDPOINT_GRAPH_V1" in js
    assert "AIWOS_VISUAL_SYSTEM_V3" in css
    assert "aiwos-graph-node" in css
    assert "animation" in css

def test_endpoint_graph_data_has_nodes_and_edges():
    data = json.loads(read("web/assets/endpoint-graph.data.json"))
    assert data["ok"] is True
    assert len(data["nodes"]) >= 6
    assert len(data["edges"]) >= 6
    endpoints = {node["endpoint"] for node in data["nodes"]}
    assert "/api/operator/run" in endpoints
    assert "/api/operator/apps" in endpoints
    assert "/api/operator/status" in endpoints

def test_visual_system_v3_metadata_local_only():
    data = json.loads(read("web/assets/visual-system-v3.meta.json"))
    assert data["local_only"] is True
    assert data["external_fonts"] is False
    assert data["external_scripts"] is False
    assert data["animations"] is True
    assert data["endpoint_graph"] is True
