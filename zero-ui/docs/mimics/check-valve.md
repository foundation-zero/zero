# Check Valve

Stateless directional mimic check valve component.

<script setup lang="ts">
import CheckValve from '@/modules/thrapp/mimics/components/check-valve/CheckValve.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`CheckValve` renders the exact Figma check valve glyph: a rectangular valve body with a diagonal slash and a directional flow indicator arrow above.

The original exported geometry is `24×32`. It is centered inside a `32×32` square viewBox using `translate(4 0)` so vertical rotations (`Up` / `Down`) do not clip.

The component is stateless and directional:

- `CHECK_VALVE_BASE_ORIENTATION` is `ComponentOrientation.Right` (the flow indicator arrow points right in the Figma drawing)
- `orientation` sets the required flow direction per instance in your mimic diagram

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required flow direction for this valve instance |

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <CheckValve :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <CheckValve :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right (base)</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <CheckValve :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <CheckValve :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

## Semantic Token Mapping

| Role | Token |
|---|---|
| Valve body fill | `--background-muted` |
| Body frame stroke + diagonal slash stroke | `--brand-muted` |
| Flow indicator arrow fill | `--foreground` |
