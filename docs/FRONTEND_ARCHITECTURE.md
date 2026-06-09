# Frontend Architecture

The console is a device-native shell with a primary rail, contextual flyout panel, workspace, and mobile bottom navigation.

## Layers

- web/index.html defines the shell and security policy.
- web/assets/console.css defines theme, layout, animation, and responsive behavior.
- web/assets/console.js defines navigation, endpoint calls, app listing, build, export, status, and theme state.
- scripts/context_packet.py creates a compressed repository context packet for handoff and recovery.

## Visual System v3

Visual System v3 adds a decoupled visual layer, animated endpoint graph, local-only graph data, and install-focused shell behavior without remote browser dependencies.
