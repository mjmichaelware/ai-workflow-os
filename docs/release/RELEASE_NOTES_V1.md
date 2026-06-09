# AI Workflow OS Release Notes v1

AI Workflow OS is a phone-first local operator console for building, proving, exporting, and packaging generated applications from an Android Termux environment.

## Included

- Local operator console
- Mobile command menu
- Agent-routed builder using installed local CLIs when available
- Generated app shell inheritance
- Recursive app factory proof to depth 4
- Android wrapper scaffold
- APK build/sign scaffold
- Final proof dashboard
- Public capability matrix
- Local-only browser assets
- Secret-clean proof flow

## Known limits

- A signed APK is not produced unless Android build tools and external signing environment variables are installed.
- Recursive inheritance is depth-limited and proof-gated, not unrestricted infinite recursion.
- Agent CLI outputs are saved as untrusted drafts and are not executed as shell.
