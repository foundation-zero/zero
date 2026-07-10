# Updating a Mimic Component

Figma is the single source of truth. When a design changes, update the component by pointing the agent at the updated Figma design — never by describing code-level changes directly.

## Prerequisites

- The [Figma MCP Bridge](/figma-mcp-bridge) must be installed and authenticated in VS Code.
- You need a Figma URL pointing to the updated design, or confirmation that the stored URL is still current.

## The FIGMA_URL Convention

Every mimic component stores its Figma source URL in a `FIGMA_URL` constant inside its `index.ts`:

```ts
// src/modules/thrapp/mimics/components/actuated-valve/index.ts
export const FIGMA_URL = "https://www.figma.com/design/...";
```

When you ask the agent to update a component, it will automatically read this URL to retrieve the latest design context — you do not need to find or paste it yourself. If the Figma URL has changed (e.g. the design was moved to a new file), include the new URL in your prompt and the agent will update the constant.

## How to Prompt the Agent

Open GitHub Copilot chat and tell the agent which component to update.

**Design changed, URL unchanged** (agent fetches the current design automatically):

> Update the Actuated Valve component from Figma. The design has changed — please re-read it and apply any differences.

**Design moved to a new Figma file:**

> Update the Actuated Valve component using this new Figma design: `<paste Figma URL>`

## What the Agent Does

1. **Reads the current component** — reads `index.ts`, the `.vue` file, and the paired docs page before changing anything.
2. **Fetches the Figma design** — uses the stored `FIGMA_URL` or the URL you provided to get the latest design context.
3. **Applies the change** — makes the minimum necessary change: geometry, color, prop, or state update.
4. **Preserves the existing API** — does not rename props, change defaults, or restructure the component unless the design change requires it.
5. **Updates docs** — reflects any behavior, state, or prop changes in the paired docs page.
6. **Validates** — runs type checking and confirms zero diagnostics before finishing.

## What to Review

After the agent finishes:

- **Changed areas** — compare the specific states or orientations that were updated against the Figma design.
- **Unchanged areas** — confirm states or orientations you did not intend to change still look correct.
- **Docs page** — verify the docs page reflects the current component behavior.
- **No hardcoded colors** — confirm no hex or rgb values were introduced.

## Common Update Scenarios

| Scenario | What to say |
|---|---|
| Design updated in place | "The Actuated Valve design has changed. Please re-read Figma and apply any differences." |
| Design moved to a new file | "The Actuated Valve component has moved to this Figma file: `<URL>`. Update the component and store the new URL." |
| Component merged or renamed in Figma | See section below. |

## When a Component Is Merged or Replaced

If Figma has consolidated two components into one (or a component has been renamed), tell the agent explicitly:

> The SwitchValve and FlowValve have been merged into a single Actuated Valve component in Figma: `<URL>`. Please merge the two Vue components into one, update the docs, and remove the old files.

The agent will:
- Merge the implementations into one canonical component.
- Update the docs to reflect the new combined component.
- Remove the old component files after verifying no remaining references.
