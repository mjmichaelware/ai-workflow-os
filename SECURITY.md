# Security Policy

## Supported versions

This project is in early public development. Security reports are accepted for the current public branch.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting if available. If it is not available, open a minimal security issue that does not disclose secrets, exploit payloads, credentials, or private user data.

## Secret handling

- Never commit API keys, tokens, passwords, service account JSON, or private credentials.
- The app may report whether an environment variable exists, but it must never print the value.
- Browser-to-Termux execution must remain allowlisted and approval-gated.
- Generated apps must inherit the same secret rules.

## Boundary

The browser sends intent. Termux performs approved material work. GitHub stores clean public source. Secrets remain outside source.
