---
description: "Use when authoring or updating layers for a mimic module (e.g. boilers, chiller, cabin). Covers the full layer-by-layer alignment workflow using Figma MCP as the design source of truth, coordinate conversion, component sizing, label nudging, and the mandatory todo + validation cycle."
name: "Mimic Module Layer Authoring"
applyTo: "src/modules/**/mimics/modules/**/*.vue"
---

# Mimic Module Layer Authoring

Use this instruction when creating or aligning layers inside a mimic module scene. A mimic module is a composed SVG scene made up of independent layer files (e.g. `Pipes.vue`, `Pumps.vue`, `Labels.vue`) that are stacked in a root module component.

Treat `figma-component-authoring.instructions.md` as the baseline for individual component standards; this document governs the module-level layer workflow.

## Non-Negotiable Rules

- **Figma MCP is the design source of truth.** Always fetch geometry from Figma before placing or moving anything.
- **Position-only changes** unless the user explicitly asks for something else. Do not change `tag-id`, `type`, `orientation`, or visual styling unless requested.
- **Per-component individual adjustments.** Never apply a uniform offset to a whole layer; each component may have its own fine-tuned position.
- **One layer at a time.** Complete, commit, and get user validation before moving to the next layer.
- **Create a todo item for every layer** at the start of the session and mark them in-progress/completed as you go.
- **Zero diagnostics** on all touched files before marking a layer done.
- **Read the file before editing.** Always read the current file contents before making changes.

## Coordinate Conversion

Figma uses absolute canvas coordinates. Module components sit at a specific canvas position. Convert like this:

```
moduleX = figmaAbsoluteX - moduleOriginX
moduleY = figmaAbsoluteY - moduleOriginY
```

Where `moduleOriginX` and `moduleOriginY` are the absolute canvas coordinates of the module's root frame in Figma. Establish these at the start of each session by fetching the module frame's position from Figma. Document the offset in session notes for reuse across all layers.

Example for the boilers module (absoluteX = -501, absoluteY = 1714):

```
moduleX = figmaAbsoluteX + 501
moduleY = figmaAbsoluteY - 1714
```

## SVG Coordinate System

- Root SVG uses a `viewBox` (e.g. `0 0 1414 854`). All positions are relative to this.
- Each layer is a child `<g>` element inside the root SVG.
- Component `x`/`y` props are **top-left anchor** coordinates.
- `ComponentOrientation` enum drives rotation. Do not change orientation unless explicitly asked.

## Session Startup Checklist

1. Fetch the module frame from Figma to confirm the coordinate offset.
2. List all layer files in the module's `layers/` directory.
3. Create a todo item for every layer:
   - `Align <LayerName> layer`
   - `Validate <LayerName> with user`
4. Ask the user if any layers should be skipped or prioritised.

## Layer Alignment Workflow

For each layer, in order:

### Step 1 — Read the current file

Read the layer file to understand existing positions before fetching Figma data.

### Step 2 — Fetch Figma geometry

Use Figma MCP to get the positions of all components in that layer. Convert coordinates using the module offset.

### Step 3 — Compare and identify deltas

Compare Figma-derived positions to what is in the file. Only change positions that are meaningfully off (>1px). Document planned changes.

### Step 4 — Apply changes

Use `multi_replace_string_in_file` for all changes in a single call. Never use sequential single-replace calls for the same layer.

### Step 5 — Validate

Mark the todo as completed and ask the user to validate visually in the browser. **Do not start the next layer until the user confirms.**

### Step 6 — Record corrections

If the user makes manual tweaks or requests adjustments, update session notes with the final accepted positions for reference.

## Component Size Changes

If Figma shows a component at a different size than what is in code:

1. Update `WIDTH`, `HEIGHT`, and any radius/offsets in the component's `index.ts`.
2. Scale SVG path data by the size ratio (e.g. ×1.5 if going from 36 to 54).
3. Adjust the layer position to preserve the visual center:
   ```
   newX = oldCenterX - newWidth / 2
   newY = oldCenterY - newHeight / 2
   ```
4. Include these changes as part of the layer's alignment step.

## Labels Layer

The labels layer requires special handling because label positions are not directly on top of their sensor; they are offset to avoid overlap.

### Rebuilding from Figma

If the labels layer is missing entries or is significantly misaligned, rebuild it from the `SensorIDs` group in the Figma frame. Map each label's Figma position through the coordinate offset.

### Directional nudging

After placing labels from raw Figma coordinates, a nudge pass is typically needed:

- Apply nudges **per label individually**, not uniformly

### Label instance types

Labels are typed by their sensor category. Use the correct instance component per label:

- `TagLabelInstance` — general equipment/valve tags
- `FlowLabelInstance` — flow sensors
- `PressureLabelInstance` — pressure sensors
- `TemperatureLabelInstance` — temperature sensors
- `FlowControlLabelInstance` — flow control valves

## Visual Comparison vs Raw Figma Coordinates

Raw Figma coordinates give a good starting point but may not produce pixel-perfect visual alignment due to SVG rendering, label sizing, or component anchor differences. When a position looks wrong after applying Figma coords:

1. Trust the user's visual judgment over raw numbers.
2. Apply small iterative nudges (1–5px) and ask the user to validate.
3. Record the accepted position for future reference.

## Fine-tuning Rules

- Nudges under 1px are usually not worth making.
- Nudges of 1–3px are fine-tuning; apply individually per component.
- Nudges over 5px suggest a coordinate conversion error — re-check the module offset.
- If a component still looks wrong after two passes, re-fetch its position from Figma and recheck the offset calculation.

## After All Layers Are Complete

- Confirm with the user that all layers are validated.
- Update repo memory if any new coordinate offsets, component sizes, or nudge patterns were discovered.
- Do not update docs unless the user asks.
