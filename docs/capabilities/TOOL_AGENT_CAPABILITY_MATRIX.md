# Tool and Agent Capability Matrix

Every tool is treated as a scoped capability, not an unlimited permission.

- **Git** (vcs): installed; network=optional; writes_repo=True
- **Python** (runtime): installed; network=none by default; writes_repo=False
- **Pytest** (test): installed; network=none; writes_repo=False
- **GitHub CLI** (platform-cli): installed; network=github; writes_repo=False
- **Cloud CLI** (platform-cli): installed; network=cloud; writes_repo=False
- **Node** (runtime): installed; network=none by default; writes_repo=False
- **NPM** (package-manager): installed; network=registry; writes_repo=True
- **Gemini CLI** (agent): installed; network=model-provider; writes_repo=requires explicit task packet
- **Claude CLI** (agent): installed; network=model-provider; writes_repo=requires explicit task packet
- **Codex CLI** (agent): missing; network=model-provider; writes_repo=requires explicit task packet
- **Curl** (http-client): installed; network=explicit URL only; writes_repo=False
