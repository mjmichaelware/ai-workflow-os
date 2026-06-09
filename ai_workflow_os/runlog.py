from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time
from typing import Any, Dict, List


@dataclass
class RunEvent:
    ts: str
    event_type: str
    message: str
    data: Dict[str, Any]


def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


class RunLog:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.run_dir / "events.jsonl"

    def append(self, event_type: str, message: str, data: Dict[str, Any] | None = None) -> None:
        event = RunEvent(ts=now_ts(), event_type=event_type, message=message, data=data or {})
        with self.path.open("a") as f:
            f.write(json.dumps(asdict(event), sort_keys=True) + "\n")

    def read(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]


def list_runs(root: Path) -> List[Dict[str, Any]]:
    runs_dir = root / "runs"
    if not runs_dir.exists():
        return []
    out = []
    for run in sorted(runs_dir.iterdir(), reverse=True):
        if run.is_dir():
            out.append({
                "run_id": run.name,
                "plan_json": str(run / "plan.json"),
                "plan_md": str(run / "plan.md"),
                "events": str(run / "events.jsonl"),
            })
    return out
