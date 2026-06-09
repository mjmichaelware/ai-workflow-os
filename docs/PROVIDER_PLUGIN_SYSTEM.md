# Provider Plugin System

Providers are registered by capability, execution surface, auth type, risk, and offline/network behavior.

Provider categories include local filesystem, shell, git, GitHub CLI, Google Cloud CLI, Secret Manager, cloud model APIs, and local model adapters.

Groq is a cloud API, not offline. Offline support requires a local model adapter.
