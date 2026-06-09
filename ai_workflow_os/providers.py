from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


@dataclass
class ProviderAdapterSpec:
    provider_id: str
    display_name: str
    capability_type: str
    execution_surface: str
    auth_type: str
    secret_ref: Optional[str]
    supports_offline: bool
    requires_network: bool
    side_effect_risk: str
    notes: str


PROVIDERS: List[ProviderAdapterSpec] = [
    ProviderAdapterSpec("local_filesystem", "Local Filesystem", "storage", "python", "none", None, True, False, "medium", "Can read and write project files with permission gates."),
    ProviderAdapterSpec("local_shell", "Local Shell", "workflow_orchestration", "subprocess", "none", None, True, False, "high", "Can run local commands only with approval."),
    ProviderAdapterSpec("git_cli", "Git CLI", "workflow_orchestration", "cli", "git_auth", None, True, False, "medium", "Can inspect status and create commits with approval."),
    ProviderAdapterSpec("github_cli", "GitHub CLI", "workflow_orchestration", "cli", "gh_auth", None, False, True, "high", "Can create PRs, issues, releases, and repo operations with approval."),
    ProviderAdapterSpec("gcloud_cli", "Google Cloud CLI", "workflow_orchestration", "cli", "gcloud_auth", None, False, True, "high", "Can manage Cloud Run, Secret Manager, Scheduler, Build, IAM with approval."),
    ProviderAdapterSpec("google_secret_manager", "Google Secret Manager", "storage", "gcloud", "iam", None, False, True, "high", "Secret values are resolved only inside approved runtime calls and never printed."),
    ProviderAdapterSpec("openai_api", "OpenAI API", "enrichment", "http", "secret_manager", "OPENAI_API_KEY", False, True, "medium", "Model provider adapter. Not a discovery source by itself."),
    ProviderAdapterSpec("gemini_api", "Gemini API", "enrichment", "http", "secret_manager", "GEMINI_API_KEY", False, True, "medium", "Model provider adapter. Not a discovery source by itself."),
    ProviderAdapterSpec("anthropic_api", "Anthropic API", "enrichment", "http", "secret_manager", "ANTHROPIC_API_KEY", False, True, "medium", "Model provider adapter. Not a discovery source by itself."),
    ProviderAdapterSpec("groq_api", "Groq API", "enrichment", "http", "secret_manager", "GROQ_API_KEY", False, True, "medium", "Cloud API. Not offline. Add local model adapter for offline mode."),
    ProviderAdapterSpec("local_model", "Local Model Adapter", "enrichment", "local_runtime", "none_or_local", None, True, False, "medium", "Placeholder interface for Ollama, llama.cpp, or future Termux-local runtimes."),
]


def list_providers() -> List[Dict[str, object]]:
    return [asdict(provider) for provider in PROVIDERS]


def get_provider(provider_id: str) -> Dict[str, object] | None:
    for provider in PROVIDERS:
        if provider.provider_id == provider_id:
            return asdict(provider)
    return None
