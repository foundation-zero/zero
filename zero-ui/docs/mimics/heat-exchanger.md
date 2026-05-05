# Heat Exchanger

Directional mimic heat exchanger component with five operational states:

- Heat A-b
- Heat a-B
- Cool A-b
- Cool a-B
- Idle

<script setup lang="ts">
import HeatExchanger from '@/modules/thrapp/mimics/components/heat-exchanger/HeatExchanger.vue'
import { HeatExchangerState } from '@/modules/thrapp/mimics/components/heat-exchanger'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`HeatExchanger` uses the exact Figma zig-zag flow geometry and maps each state to semantic design tokens.

The component is directional and follows the shared mimic orientation convention:

- `HEAT_EXCHANGER_BASE_ORIENTATION` defines the drawing direction from Figma (`Right`)
- `orientation` sets the required direction for each instance in a mimic diagram

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `state` | `HeatExchangerState` | `HeatExchangerState.Idle` | State variant (`heat-a-b`, `heat-a-B`, `cool-a-b`, `cool-a-B`, `idle`) |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required direction for this instance |

## State Variants

<div class="grid grid-cols-2 md:grid-cols-5 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.HeatAB" />
    </div>
    <span class="text-sm font-mono">Heat A-b</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.HeataB" />
    </div>
    <span class="text-sm font-mono">Heat a-B</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.CoolAB" />
    </div>
    <span class="text-sm font-mono">Cool A-b</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.CoolaB" />
    </div>
    <span class="text-sm font-mono">Cool a-B</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.Idle" />
    </div>
    <span class="text-sm font-mono">Idle</span>
  </div>
</div>

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.HeatAB" :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.HeatAB" :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.HeatAB" :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.HeatAB" :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

```vue
<script setup lang="ts">
import HeatExchanger from '@/modules/thrapp/mimics/components/heat-exchanger/HeatExchanger.vue'
import { HeatExchangerState } from '@/modules/thrapp/mimics/components/heat-exchanger'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

<template>
  <div class="flex gap-4">
    <HeatExchanger :state="HeatExchangerState.HeatAB" :orientation="ComponentOrientation.Right" />
    <HeatExchanger :state="HeatExchangerState.CoolaB" :orientation="ComponentOrientation.Down" />
    <HeatExchanger :state="HeatExchangerState.Idle" :orientation="ComponentOrientation.Left" />
  </div>
</template>
```

## Semantic Token Mapping

- `heat-a-b`
  - shell: `--attention`
  - left: `--heating-medium`
  - right: `--heating-low`
- `heat-a-B`
  - shell: `--attention`
  - left: `--cooling-medium`
  - right: `--cooling-medium`
- `cool-a-b`
  - shell: `transparent` (hidden)
  - left: `--cooling-medium`
  - right: `--cooling-low`
- `cool-a-B`
  - shell: `--attention`
  - left: `--cooling-low`
  - right: `--cooling-medium`
- `idle`
  - shell: `--attention-dull`
  - left: `--disabled-foreground`
  - right: `--disabled-foreground`
