# Public Surface Hygiene Standard

Browser-executed files must remain local-only and brand-neutral.

## Browser-executed surfaces

- web/index.html
- web/assets/console.css
- web/assets/console.js
- web/sw.js

These files must not load remote fonts, remote scripts, remote style sheets, or remote browser resources.

## Runtime source surfaces

Python code may contain localhost URLs for local server startup, local proof scripts, and local health checks. Non-local URLs must not appear in executable runtime surfaces unless the action is explicit, documented, and not browser-triggered.

Run:

python3 scripts/verify_public_surface.py
