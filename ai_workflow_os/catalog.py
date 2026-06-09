CATALOG = {
    "name": "AI Workflow OS",
    "purpose": "generic AI-agent workflow control plane",
    "agent_roles": [
        "architect",
        "security_auditor",
        "frontend_contract_auditor",
        "backend_contract_auditor",
        "provider_registry_engineer",
        "test_engineer",
        "release_manager",
        "handoff_manager"
    ],
    "workflow_documents": [
        "APP_MISSION.md",
        "SESSION_STATE.md",
        "CANONICAL_RESOLVED_SPEC.md",
        "CURRENT_CODE_MAP.md",
        "BUG_LEDGER.md",
        "FINAL_PATCH_PLAN.md",
        "FINAL_PROOF_REPORT.md"
    ],
    "standards": [
        "no_secrets",
        "no_blind_patching",
        "inspect_before_patch",
        "compile_before_commit",
        "proof_before_deploy",
        "separate_generic_workflow_from_app_data",
        "ui_backend_contract_parity",
        "provider_registry_pattern",
        "termux_arm64_safe_commands"
    ],
    "provider_capability_types": [
        "discovery",
        "enrichment",
        "classification",
        "extraction",
        "ranking",
        "geocoding",
        "notification",
        "storage",
        "visualization",
        "workflow_orchestration"
    ],
    "safe_default_commands": [
        "doctor",
        "catalog",
        "status",
        "init-project",
        "export-packet",
        "serve"
    ]
}
