# Pipe Heat Exchanger

Stateless directional mimic pipe heat exchanger component.

<script setup lang="ts">
import PipeHeatExchanger from '@/modules/thrapp/mimics/components/pipe-heat-exchanger/PipeHeatExchanger.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`PipeHeatExchanger` renders the standard pipe heat exchanger schematic symbol using exact Figma geometry. The component is stateless — it carries no operational state — but is directional and follows the shared mimic orientation convention:

- `PIPE_HEAT_EXCHANGER_BASE_ORIENTATION` defines the drawing direction from Figma (`Right`)
- `orientation` sets the required direction for each instance in a mimic diagram

The geometry is a 51 × 22 px pipe shape centered inside a 52 × 52 px square viewBox so that all four 90° rotations render within the same bounding box.

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required direction for this instance |

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right (base)</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

## Semantic Token Mapping

The component uses two tokens regardless of orientation:

| Role | Token |
|---|---|
| Pipe body fill | `--background` |
| All strokes | `--attention` |
