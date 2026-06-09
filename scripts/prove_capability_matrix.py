
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_workflow_os.capability_matrix import write_capability_matrix


def main() -> int:
    payload = write_capability_matrix()
    json_path = ROOT / "docs" / "capabilities" / "TOOL_AGENT_CAPABILITY_MATRIX.json"
    md_path = ROOT / "docs" / "capabilities" / "TOOL_AGENT_CAPABILITY_MATRIX.md"
    ok = (
        payload.get("ok") is True
        and payload.get("broad_permissions") is False
        and payload.get("keys_printed") is False
        and len(payload.get("capabilities", [])) >= 8
        and json_path.exists()
        and md_path.exists()
    )
    result = {
        "ok": ok,
        "capability_count": len(payload.get("capabilities", [])),
        "json": str(json_path),
        "markdown": str(md_path),
        "keys_printed": False,
        "broad_permissions": False,
    }
    print(json.dumps(result, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
