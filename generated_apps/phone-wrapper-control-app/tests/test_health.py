from pathlib import Path
def test_manifest_exists():
    assert Path(__file__).resolve().parents[1].joinpath("APP_MANIFEST.json").exists()
