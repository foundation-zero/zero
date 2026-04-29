---
description: "Use when creating new Figma-derived components or mimic components from scratch. Covers the full Figma MCP authoring workflow, exact geometry capture, semantic token mapping, colocated index.ts constants, and required docs updates."
name: "Figma Component Authoring"
applyTo: "src/modules/thrapp/mimics/components/**/index.ts, src/modules/thrapp/mimics/components/**/*.vue, docs/mimics/*.md"
---

# Figma Component Authoring

Use this instruction when implementing new Figma-backed mimic components in Zero UI.
It is written as a standalone rule set for agents working in this repository.

## Scope

Use this for domain-specific mimic components in:

- `src/modules/thrapp/mimics/components/**`

These components should be small, composable primitives intended for larger mimic scenes.

## Non-Negotiable Rules

- Pure SVG template only for all components.
- No HTML wrappers (`div`, `span`, etc.) around components.
- One base geometry when states are rotational variants.
- Semantic tokens only for color. Do not leave hardcoded hex or rgb values in the final component.
- Typed state props with explicit union types.
- Exact Figma geometry from exported vectors. Do not hand-draw approximations.
- Documentation required for every component with examples and token notes.
- Zero diagnostics on all touched files before finishing.
- All text labels as SVG text unless exact glyph shapes are required, then use path data from Figma.
- Created files must be formatted and linted according to project standards.
- State-to-color mapping should use a computed property or shared helper driven by a `Record<Type, string>`.
- Types, constants, dimensions, and design references should live in the component folder `index.ts`.
- Use shared mimic composables such as `useStateColor` and `useOrientation` instead of re-implementing local helpers.
- For directional components, include a typed `orientation: ComponentOrientation` prop and rotate the SVG group around the icon center.

## Design Reference Convention

Add a component-local Figma reference in the component `index.ts` whenever a stable design URL exists:

```ts
export const FIGMA_URL = "https://www.figma.com/design/...";
```

Keep this updated when a component is intentionally re-pointed to a new Figma source.

## Authoring Process

### 1. Get design context from Figma

- Call `mcp_figma_get_design_context` for the target node.
- Identify all relevant state variants in the selected frame or component.
- Record the node IDs for those variants when multiple states are involved.

### 2. Export exact SVG vectors from Figma

- Use `mcp_figma_use_figma` with `exportAsync({ format: 'SVG' })` on the relevant nodes.
- Capture raw SVG for all relevant states.
- Prefer exact path, rect, circle, and text geometry from those exports.

### 3. Derive a reusable geometry model

- Compare exported state SVGs.
- If states differ only by rotation, position, or color:
  - Keep one canonical geometry.
  - Apply rotation around the component center for state changes.
  - Move auxiliary markers only when the design requires it.

### 4. Map colors to semantic tokens

- Replace hardcoded colors with semantic CSS variables from `src/assets/index.css`.
- Match tokens to design intent, for example `constructive`, `warning`, `destructive`, `attention`.

### 5. Implement in the component folder

- Place the component under `src/modules/thrapp/mimics/components/<component-name>/`.
- Add or maintain a colocated `index.ts`.
- Use `<script setup lang="ts">`.
- Define exported prop contracts in `index.ts`, then consume them with `defineProps` in the `.vue` file.
- Use `toRefs(props)` when passing values to shared composables.
- Keep the template strictly SVG.
- Bind SVG sizing to exported width and height constants.

### 6. Validate and refine

- Run diagnostics on touched files.
- Compare against the Figma screenshot or design context.
- Fine-tune viewBox, dimensions, rotation origin, text alignment, and stroke rendering.

### 7. Document the component

- Add or update the paired docs page in `docs/mimics/`.
- Include overview, props table, state examples, and semantic token notes.
- Ensure the page is linked from the Mimics docs navigation.

## Review Checklist

Before considering a component complete, verify all items:

- SVG proportions match Figma.
- State transitions match Figma orientation and marker placement.
- No hardcoded hex or rgb colors remain.
- Semantic tokens reflect design intent.
- Component compiles with zero diagnostics.
- Documentation exists and is linked from the Mimics section.

## Common Pitfalls

- Building approximate geometry manually instead of exporting exact paths.
- Using multiple SVG trees when one rotated geometry is enough.
- Mixing semantic tokens with leftover hardcoded colors.
- Adding HTML wrappers around what should be pure SVG output.
