# Authoring a New Mimic Component

This page explains how to use GitHub Copilot to create a new mimic component from a Figma design. The agent handles the full implementation — your job is to provide the Figma URL and review the result.

## Prerequisites

- The [Figma MCP Bridge](/figma-mcp-bridge) must be installed and authenticated in VS Code.
- You need a Figma URL pointing to the specific component or frame you want to implement.
- The URL should be a dev-mode link: open the component in Figma, switch to Dev mode, and copy the link from the address bar or the node inspector.

## How to Prompt the Agent

Open GitHub Copilot chat and ask it to create the component. Keep the prompt short — the agent instruction files handle all the implementation rules automatically.

**Prompt:**

> Create a new mimic component from this Figma design: `<paste Figma URL>`

The agent will then work through the implementation without further input. You can watch its progress in the chat panel.

## What the Agent Does

1. **Reads the Figma design** — fetches geometry, colors, and state variants from the linked node.
2. **Exports exact SVG paths** — uses the Figma API to get vector data for all states.
3. **Derives a geometry model** — reduces multiple states to one canonical shape with rotation or color changes where possible.
4. **Maps colors to semantic tokens** — replaces Figma hex values with design-system CSS variables.
5. **Creates the component files** — places the `.vue` file and a colocated `index.ts` under `src/modules/thrapp/mimics/components/<name>/`.
6. **Stores the Figma URL** — adds a `FIGMA_URL` constant in `index.ts` so future updates have a known reference point.
7. **Validates** — runs type checking on all touched files and confirms zero diagnostics.
8. **Creates the docs page** — adds an entry under `docs/mimics/` with a props table and state examples.

## What to Review

Once the agent is done, check the following before committing:

- **SVG proportions** — compare the rendered component against the Figma design visually.
- **State colors** — confirm each state color matches the Figma intent.
- **Orientation** — if the component is directional, verify all four orientations render correctly.
- **No hardcoded colors** — search for any remaining hex or rgb values in the component file.
- **Docs page** — open the docs locally and confirm the component page renders with working examples.

## Component Location

All mimic components live under:

```
src/modules/thrapp/mimics/components/<component-name>/
  index.ts        ← props, enums, constants, FIGMA_URL
  ComponentName.vue
```

Docs pages live under:

```
docs/mimics/<component-name>.md
```

## Shared Utilities

The agent will use these shared composables automatically — you do not need to mention them:

| Utility | Purpose |
|---|---|
| `useOrientation` | Computes rotation angle from `ComponentOrientation` |
| `createSizeAndViewbox` | Derives SVG size and viewBox from width/height constants |
| `ComponentOrientation` | Typed enum for directional components |
| `CLOCKWISE_ORIENTATIONS` | Ordered orientation array for rotation math |

## What Goes in index.ts vs the Template

Only extract SVG geometry to `index.ts` when the value is **computed** or **shared across files**.

| Geometry type | Where it lives |
|---|---|
| `d` attribute on a static path | Inline in the template — do not extract |
| `d` attribute that is computed per state | Computed property or `Record` in `index.ts` |
| `width`, `height` (component dimensions) | Constants in `index.ts` — used for `createSizeAndViewbox` |
| `rx`, `ry`, `cx`, `cy`, `r` on static shapes | Inline in the template |
| Static `rect` / `circle` geometry shared across states | Inline in the template |

The rule: if a geometry value never changes and is only used in the template, write it there directly.

## Orientation Convention (Required)

All directional mimic components must include both a base orientation constant and an instance orientation prop:

- `*_BASE_ORIENTATION` in `index.ts` describes how the component is drawn in Figma (for example `ComponentOrientation.Up` or `ComponentOrientation.Right`).
- `orientation` prop describes the required direction for the component instance in the mimic diagram.
- Rendered rotation should always be computed with `useOrientation(orientation, *_BASE_ORIENTATION)`.

When state variants are rotational changes of the same geometry, keep one canonical geometry and derive state rotation from the requested `orientation`:

- Start from the requested instance `orientation`.
- Apply state-specific orientation offsets (for example with `getNextOrientation`).
- Pass the resulting orientation into `useOrientation` with the same base orientation constant.

This keeps component APIs consistent across mimics and prevents state-specific geometry duplication.
