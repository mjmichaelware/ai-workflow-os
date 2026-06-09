#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_workflow_os.registry_spine.spine import build_registry, dispatch, rebuild

def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        print("Commands: manifest, rebuild, dispatch <action_id> [json_payload]")
        return 0

    if args[0] == "manifest":
        print(json.dumps(build_registry().manifest(), indent=2, sort_keys=True))
        return 0

    if args[0] == "rebuild":
        print(json.dumps(rebuild(), indent=2, sort_keys=True))
        return 0

    if args[0] == "dispatch":
        if len(args) < 2:
            print("missing action_id", file=sys.stderr)
            return 2
        payload = json.loads(args[2]) if len(args) > 2 else {}
        print(json.dumps(dispatch(args[1], payload, source="cli"), indent=2, sort_keys=True))
        return 0

    print("unknown command: " + args[0], file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
