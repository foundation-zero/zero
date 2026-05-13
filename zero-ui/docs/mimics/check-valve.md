# Check Valve

Stateless directional mimic check valve component.

<script setup lang="ts">
import CheckValve from '@/modules/thrapp/mimics/components/check-valve/CheckValve.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`CheckValve` renders the exact Figma check valve glyph: a rectangular valve body with a diagonal slash and a directional flow indicator arrow above.

The original exported geometry is `24×32`. It is centered inside a `32×32` square viewBox using `translate(4 0)` so vertical rotations (`Up` / `Down`) do not clip.

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Up` | Rotation of the valve relative to its base orientation |

## Orientation Examples
<div>
  <div class="flex flex-col items-center justify-center gap-2">
      <CheckValve :orientation="ComponentOrientation.Up" />
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
