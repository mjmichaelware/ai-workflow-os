
# Visual System v3 Standard

AI Workflow OS must keep the interface decoupled, local-only, animated, responsive, and endpoint-backed.

## Required surfaces

- Design tokens and animation in web/assets/visual-system-v3.css
- Endpoint graph behavior in web/assets/endpoint-graph.js
- Endpoint graph data in web/assets/endpoint-graph.data.json
- Metadata in web/assets/visual-system-v3.meta.json
- Tests for local-only assets and graph surface
- No remote runtime fonts
- No remote browser scripts
- No secret values
- No competitor style language

## Product direction

Every data point should be expressible as a node, every node should point to a local endpoint or local proof artifact, and every visible action should map to a verified command path.
