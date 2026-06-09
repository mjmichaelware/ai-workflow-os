# Privacy

AI Workflow OS is local-first.

## Local operator

The console talks to localhost endpoints on the user-owned device.

## Secrets

The app may report whether a secret environment variable exists. It must never print, store, or commit secret values.

## Network

The local console must not call external networks from the browser UI. Public research and GitHub operations are explicit terminal-side actions.
