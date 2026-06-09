# APK Build/Sign Pipeline v1 Standard

## Rules

- Never commit keystores.
- Never print signing passwords.
- Never store signing secrets in generated scaffold files.
- Report environment variable presence only.
- Build, sign, and verify are separate scripts.
- APK generation remains proof-gated.
- Missing Android tooling must be reported, not hidden.
