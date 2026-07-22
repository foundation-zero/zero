# Flow Sensor

Stateless directional mimic flow sensor component.

<script setup lang="ts">
import FlowSensor from '@/modules/thrapp/mimics/components/flow-sensor/FlowSensor.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`FlowSensor` renders the exact Figma flow sensor glyph — a circular badge labelled "FLOW" connected by a stem to a lower display box containing "≈≈" (approximate flow marks).

The original exported geometry is `24×40`. It is centered inside a `40×40` square viewBox using `translate(8 0)` so horizontal rotations (`Left` / `Right`) do not clip.

The component is stateless and directional:

- `FLOW_SENSOR_BASE_ORIENTATION` is `ComponentOrientation.Down` (the stem points down in the Figma drawing)
- `orientation` sets the required direction per instance in your mimic diagram

## Props

| Prop          | Type                   | Default                     | Description                                 |
| ------------- | ---------------------- | --------------------------- | ------------------------------------------- |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Down` | Required direction for this sensor instance |

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <FlowSensor :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <FlowSensor :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <FlowSensor :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down (base)</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <FlowSensor :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

## Semantic Token Mapping

| Role                                 | Token          |
| ------------------------------------ | -------------- |
| Circular badge fill + lower box fill | `--muted`      |
| All strokes                          | `--attention`  |
| "FLOW" glyph fill + "≈≈" glyph fill  | `--foreground` |
