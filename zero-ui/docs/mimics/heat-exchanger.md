# Heat Exchanger

Directional mimic heat exchanger component with three operational states:

- Heating
- Cooling
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
| `state` | `HeatExchangerState` | `HeatExchangerState.Idle` | State variant (`heating`, `cooling`, `idle`) |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required direction for this instance |

## State Variants

<div class="grid grid-cols-2 md:grid-cols-3 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.Heating" />
    </div>
    <span class="text-sm font-mono">Heating</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.Cooling" />
    </div>
    <span class="text-sm font-mono">Cooling</span>
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
      <HeatExchanger :state="HeatExchangerState.Heating" :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.Heating" :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.Heating" :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatExchangerState.Heating" :orientation="ComponentOrientation.Left" />
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
    <HeatExchanger :state="HeatExchangerState.Heating" :orientation="ComponentOrientation.Right" />
    <HeatExchanger :state="HeatExchangerState.Cooling" :orientation="ComponentOrientation.Down" />
    <HeatExchanger :state="HeatExchangerState.Idle" :orientation="ComponentOrientation.Left" />
  </div>
</template>
```

## Semantic Token Mapping

- `heating`
  - shell fill: `--inverse-muted`
  - shell stroke: `--attention-dull`
  - left: `--heating-medium`
  - right: `--heating-medium`
- `cooling`
  - shell fill: `--inverse-muted`
  - shell stroke: `--attention-dull`
  - left: `--cooling-medium`
  - right: `--cooling-medium`
- `idle`
  - shell fill: `--inverse-muted`
  - shell stroke: `--attention`
  - left: `--disabled-foreground`
  - right: `--disabled-foreground`
