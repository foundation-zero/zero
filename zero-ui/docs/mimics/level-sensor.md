# Level Sensor

Stateless directional mimic level sensor component.

<script setup lang="ts">
import LevelSensor from '@/modules/thrapp/mimics/components/level-sensor/LevelSensor.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`LevelSensor` renders the exact Figma level sensor glyph: a circular badge with `LS` mark and a connecting stem.

The original exported geometry is `24×30`. It is centered inside a `32×32` square viewBox using `translate(4 1)` so horizontal rotations (`Left` / `Right`) do not clip.

The component is stateless and directional:

- `LEVEL_SENSOR_BASE_ORIENTATION` is `ComponentOrientation.Down` (the stem points down in the Figma drawing)
- `orientation` sets the required direction per instance in your mimic diagram

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Down` | Required direction for this sensor instance |

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <LevelSensor :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <LevelSensor :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <LevelSensor :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down (base)</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <LevelSensor :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

## Semantic Token Mapping

| Role | Token |
|---|---|
| Sensor body fill | `--background-muted` |
| Body frame stroke + stem stroke | `--attention` |
| `LS` glyph fill | `--foreground` |
