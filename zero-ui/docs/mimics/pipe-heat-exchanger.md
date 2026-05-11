# Pipe Heat Exchanger

Directional mimic pipe heat exchanger component with operational states.

<script setup lang="ts">
import PipeHeatExchanger from '@/modules/thrapp/mimics/components/pipe-heat-exchanger/PipeHeatExchanger.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
import { PipeHeatExchangerState } from '@/modules/thrapp/mimics/components/pipe-heat-exchanger/index'
</script>

## Overview

`PipeHeatExchanger` renders the standard pipe heat exchanger schematic symbol using exact Figma geometry with visual state indication. The component is directional and follows the shared mimic orientation convention:

- `PIPE_HEAT_EXCHANGER_BASE_ORIENTATION` defines the drawing direction from Figma (`Right`)
- `orientation` sets the required direction for each instance in a mimic diagram
- `state` controls the visual appearance to indicate operational status (Idle, Heating, Cooling)

The geometry is a 51 × 22 px pipe shape centered inside a 52 × 52 px square viewBox so that all four 90° rotations render within the same bounding box.

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required direction for this instance |
| `state` | `PipeHeatExchangerState` | `PipeHeatExchangerState.Idle` | Operational state (Idle, Heating, Cooling) |

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

## State Examples

<div class="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :state="PipeHeatExchangerState.Idle" />
    </div>
    <span class="text-sm font-mono">Idle</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :state="PipeHeatExchangerState.Heating" />
    </div>
    <span class="text-sm font-mono">Heating</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PipeHeatExchanger :state="PipeHeatExchangerState.Cooling" />
    </div>
    <span class="text-sm font-mono">Cooling</span>
  </div>
</div>

## Semantic Token Mapping

The component uses a two-tone state treatment:

| Role | Token |
|---|---|
| All strokes | `--attention` |
| Outer body fill (all states) | `--background` |
| Inner channel fill (Idle) | `none` |
| Inner channel fill (Heating) | `--heating-medium` |
| Inner channel fill (Cooling) | `--cooling-medium` |
