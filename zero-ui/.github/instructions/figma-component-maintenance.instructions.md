---
description: "Use when updating existing Figma-derived components, mimic components, or their paired docs. Covers minor follow-up changes, using a component-local FIGMA_URL in index.ts, preserving existing APIs, and updating docs with the component change."
name: "Figma Component Maintenance"
applyTo: "src/modules/**/components/**/index.ts, src/modules/**/components/**/*.vue, docs/components/*.md, docs/mimics/*.md"
---

# Figma Component Maintenance

Use this workflow when the user asks to adjust an existing Figma-backed component rather than creating a brand new one.

Treat `figma-component-authoring.instructions.md` as the baseline implementation standard, then apply the maintenance-specific rules below.

## Starting Point

- Treat the local component as the source of truth for implementation patterns.
- First read the component `index.ts`, main `.vue` file, paired docs page, and the relevant agent instructions before changing anything.
- Check the component `index.ts` for an exported `FIGMA_URL` constant.
- If `FIGMA_URL` exists, use that URL as the default Figma reference for future updates.

## Figma URL Convention

- Preferred convention in component `index.ts`:

```ts
export const FIGMA_URL = "https://www.figma.com/design/...";
```

- When the user provides a new Figma URL for an existing component, add or update `FIGMA_URL` in that component `index.ts` as part of the change, unless the user says not to.
- If a component does not yet have an `index.ts`, create one when touching that component if it helps keep props, enums, constants, and `FIGMA_URL` together.

## Update Rules

- Follow all non-negotiable authoring rules unless the user explicitly asks for a deliberate deviation.
- Reuse existing local subcomponents, shared primitives, tokens, enums, and helpers before introducing new structures.
- Keep the public API stable unless the requested design change requires an API change.
- For small visual or layout changes, prefer editing the existing component over creating replacement components.
- Preserve semantic token usage and existing naming patterns.
- Preserve exact SVG geometry for mimic components unless the Figma change requires a geometry update.
- If a component has been merged or superseded, update docs and references to the new canonical component and remove stale component files only after verifying references.

## Docs Sync

- When component behavior, states, variants, or props change, update the paired docs page in the same task.
- Remove stale examples when a component is merged, renamed, or replaced.
- Keep examples aligned with the real exported API, enum names, and default values.

## Validation

- Run focused diagnostics or typecheck after edits.
- Prefer narrow validation for the touched slice before broader checks.
- If old component files or docs are superseded by a merged component, remove them and verify references are updated.
