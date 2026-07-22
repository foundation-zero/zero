# Temperature Sensor

Stateless directional mimic temperature sensor component.

<script setup lang="ts">
import TemperatureSensor from '@/modules/thrapp/mimics/components/temperature-sensor/TemperatureSensor.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`TemperatureSensor` renders the exact Figma sensor glyph and stem geometry as a compact SVG primitive.

The original exported sensor geometry is centered inside a `32 x 32` square viewBox so horizontal rotations (`Left` / `Right`) do not clip.

The component is stateless and directional:

- `TEMPERATURE_SENSOR_BASE_ORIENTATION` is `ComponentOrientation.Down` (the stem points down in the Figma drawing)
- `orientation` sets the required direction per instance in your mimic diagram

## Props

| Prop          | Type                   | Default                     | Description                                 |
| ------------- | ---------------------- | --------------------------- | ------------------------------------------- |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Down` | Required direction for this sensor instance |

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <TemperatureSensor :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <TemperatureSensor :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <TemperatureSensor :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down (base)</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <TemperatureSensor :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

## Semantic Token Mapping

| Role                         | Token          |
| ---------------------------- | -------------- |
| Sensor body fill             | `--muted`      |
| Sensor frame stroke          | `--attention`  |
| Diagonal slash + stem stroke | `--attention`  |
| Glyph marks (`t`, `l`) fill  | `--foreground` |
