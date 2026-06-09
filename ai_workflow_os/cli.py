from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import scan_project, install_into_project, export_packet, catalog_json
from .executor import execute_plan
from .orchestrator import WorkflowAgent, save_plan
from .permissions import default_policy_json
from .providers import list_providers
from .secrets import secret_status


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path.cwd()
    required = ["README.md", "ai_workflow_os/core.py", "ai_workflow_os/server.py", "ai_workflow_os/cli.py", "ai_workflow_os/providers.py", "ai_workflow_os/secrets.py", "workflow/MASTER_AGENT_START_PROMPT.md", "standards/OMEGA_ALPHA_STANDARD.md"]
    missing = [p for p in required if not (root / p).exists()]
    print("AI Workflow OS doctor")
    print(f"root={root}")
    if missing:
        print("missing:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("PASS: core files exist")
    return 0

def cmd_catalog(args: argparse.Namespace) -> int:
    print(catalog_json())
    return 0

def cmd_providers(args: argparse.Namespace) -> int:
    print(json.dumps({"providers": list_providers()}, indent=2))
    return 0

def cmd_permissions(args: argparse.Namespace) -> int:
    print(json.dumps(default_policy_json(), indent=2))
    return 0

def cmd_secret_status(args: argparse.Namespace) -> int:
    print(json.dumps(secret_status(args.secret, project_id=args.project), indent=2))
    return 0

def cmd_status(args: argparse.Namespace) -> int:
    print(json.dumps(scan_project(Path(args.target)).__dict__, indent=2))
    return 0

def cmd_init_project(args: argparse.Namespace) -> int:
    print(json.dumps(install_into_project(Path(args.target), app_name=args.name), indent=2))
    return 0

def cmd_export(args: argparse.Namespace) -> int:
    archive = export_packet(Path(args.target), Path(args.out))
    print(f"exported={archive}")
    return 0

def cmd_agent_plan(args: argparse.Namespace) -> int:
    agent = WorkflowAgent()
    plan = agent.create_app_plan(args.prompt, target=args.target, mode="dry_run")
    plan_path = save_plan(plan, Path(args.out))
    print(json.dumps({"plan_path": str(plan_path), "run_id": plan.run_id, "mode": plan.mode}, indent=2))
    return 0

def cmd_agent_run(args: argparse.Namespace) -> int:
    print(json.dumps(execute_plan(Path(args.plan), approve=args.approve), indent=2))
    return 0

def cmd_serve(args: argparse.Namespace) -> int:
    from .server import run_server
    run_server(host=args.host, port=args.port)
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-workflow-os", description="AI Workflow OS CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("doctor"); p.set_defaults(func=cmd_doctor)
    p = sub.add_parser("catalog"); p.set_defaults(func=cmd_catalog)
    p = sub.add_parser("providers"); p.set_defaults(func=cmd_providers)
    p = sub.add_parser("permissions"); p.set_defaults(func=cmd_permissions)
    p = sub.add_parser("secret-status"); p.add_argument("secret"); p.add_argument("--project", default=None); p.set_defaults(func=cmd_secret_status)
    p = sub.add_parser("status"); p.add_argument("target", nargs="?", default="."); p.set_defaults(func=cmd_status)
    p = sub.add_parser("init-project"); p.add_argument("target"); p.add_argument("--name", default="REPLACE_ME"); p.set_defaults(func=cmd_init_project)
    p = sub.add_parser("export-packet"); p.add_argument("target"); p.add_argument("--out", default=str(Path.home() / "storage/downloads")); p.set_defaults(func=cmd_export)
    p = sub.add_parser("agent-plan"); p.add_argument("prompt"); p.add_argument("--target", default="."); p.add_argument("--out", default="runs"); p.set_defaults(func=cmd_agent_plan)
    p = sub.add_parser("agent-run"); p.add_argument("plan"); p.add_argument("--approve", action="store_true"); p.set_defaults(func=cmd_agent_run)
    p = sub.add_parser("serve"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8765); p.set_defaults(func=cmd_serve)
    return parser

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
