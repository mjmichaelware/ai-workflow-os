# Generated App Shell Inheritance v2 Standard

Every generated app must inherit the AI Workflow OS app shell.

## Required files

- APP_MANIFEST.json
- README.md
- app.py
- builder.py
- web/index.html
- web/manifest.webmanifest
- web/sw.js
- web/assets/app.css
- web/assets/app.js
- web/assets/icon.svg
- android_wrapper/android_wrapper.json
- proof/app_shell_proof.json
- proof/app_shell_packet.json

## Rules

- No secret values.
- No broad permissions.
- Installable PWA shell first.
- Native Android wrapper scaffold only until explicit signing stage.
- Every generated app can create a child app through a proof-gated builder.
