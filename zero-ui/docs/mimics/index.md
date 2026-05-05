# Mimic Components

Mimic components are domain-specific visual components used in THRAPP mimic diagrams.

They are intentionally compact, SVG-first, and designed to map closely to process schematics while still following Zero UI semantic design tokens.

## Available Mimic Components

- [Actuated Valve](/mimics/actuated-valve) - Unified switch + flow-control valve component for mimic diagrams
- [Pump](/mimics/pump) - Four-state pump icon for mimic diagrams (Active, Transient, Closed, Alarm)
- [Heat Exchanger](/mimics/heat-exchanger) - Three-state directional heat exchanger icon for mimic diagrams
- [Pipe Heat Exchanger](/mimics/pipe-heat-exchanger) - Stateless directional pipe heat exchanger icon for mimic diagrams

## Authoring

- [Mimic Component Authoring Workflow](/mimics/authoring-workflow) - Canonical process for implementing Figma-based mimic components

## Design Principles

- **Pure SVG output** for precision and portability in mimic layouts
- **Semantic color tokens** for theme consistency (`attention`, `attention-dull`, etc.)
- **State-driven visuals** where rotation and token changes represent operational state
- **Small, composable primitives** intended for larger mimic scenes
