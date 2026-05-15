# Heat Exchanger

Directional mimic heat exchanger symbol composed from a shell component and two child port elements.

<script setup lang="ts">
import HeatExchanger from '@/modules/thrapp/mimics/components/heat-exchanger/HeatExchanger.vue'
import HeatExchangerPort from '@/modules/thrapp/mimics/components/heat-exchanger/HeatExchangerPort.vue'
import { ComponentOrientation, HeatingState } from '@/modules/thrapp/mimics/components'
import { HeatExchangerPortOrientation } from '@/modules/thrapp/mimics/components/heat-exchanger'
</script>

## Overview

`HeatExchanger` renders the shell of the exchanger. The flow geometry is now composed from two explicit `HeatExchangerPort` children, one for side `a` and one for side `b`.

Use the shell component as the root wrapper and pass both child ports through its default slot to describe the active flow on each side.

The updated Figma geometry uses a 56 × 56 footprint with a centered 48 × 48 shell and 8 px connector circles.

The component is directional and follows the shared mimic orientation convention:

- `HEAT_EXCHANGER_BASE_ORIENTATION` defines the drawing direction from Figma (`Right`)
- `orientation` on `HeatExchanger` sets the required direction for the shell in a mimic diagram
- `orientation` on `HeatExchangerPort` chooses the connector layout for that port (`Top` or `Side`)

## Shell Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `state` | `HeatingState` | `HeatingState.Idle` | Shell stroke state. `Idle` uses the idle shell color, any non-idle state uses the active shell color |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required direction for the exchanger shell |

## Port Props

Render exactly two child ports for a complete exchanger symbol:

- `side="a"`
- `side="b"`

| Prop | Type | Default | Description |
|---|---|---|---|
| `side` | `'a' \| 'b'` | Required | Selects which side of the exchanger the port renders on |
| `state` | `HeatingState` | Required | Controls the zig-zag port stroke color |
| `orientation` | `HeatExchangerPortOrientation` | Required | Chooses the connector placement for that port: `Top` or `Side` |

## Composed Examples

<div class="grid grid-cols-2 md:grid-cols-3 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.HeatingMedium">
        <HeatExchangerPort side="a" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Side" />
        <HeatExchangerPort side="b" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Side" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Both Sides Heating</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.CoolingMedium">
        <HeatExchangerPort side="a" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Top" />
        <HeatExchangerPort side="b" :state="HeatingState.CoolingMedium" :orientation="HeatExchangerPortOrientation.Side" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Mixed Port States</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.Idle">
        <HeatExchangerPort side="a" :state="HeatingState.Idle" :orientation="HeatExchangerPortOrientation.Top" />
        <HeatExchangerPort side="b" :state="HeatingState.Idle" :orientation="HeatExchangerPortOrientation.Top" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Both Sides Idle</span>
  </div>
</div>

## Shell Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.HeatingMedium" :orientation="ComponentOrientation.Up">
        <HeatExchangerPort side="a" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Top" />
        <HeatExchangerPort side="b" :state="HeatingState.HeatingHigh" :orientation="HeatExchangerPortOrientation.Top" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.HeatingMedium" :orientation="ComponentOrientation.Right">
        <HeatExchangerPort side="a" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Top" />
        <HeatExchangerPort side="b" :state="HeatingState.HeatingHigh" :orientation="HeatExchangerPortOrientation.Top" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.HeatingMedium" :orientation="ComponentOrientation.Down">
        <HeatExchangerPort side="a" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Top" />
        <HeatExchangerPort side="b" :state="HeatingState.HeatingHigh" :orientation="HeatExchangerPortOrientation.Top" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <HeatExchanger :state="HeatingState.HeatingMedium" :orientation="ComponentOrientation.Left">
        <HeatExchangerPort side="a" :state="HeatingState.HeatingMedium" :orientation="HeatExchangerPortOrientation.Top" />
        <HeatExchangerPort side="b" :state="HeatingState.HeatingHigh" :orientation="HeatExchangerPortOrientation.Top" />
      </HeatExchanger>
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

```vue
<script setup lang="ts">
import HeatExchanger from '@/modules/thrapp/mimics/components/heat-exchanger/HeatExchanger.vue'
import HeatExchangerPort from '@/modules/thrapp/mimics/components/heat-exchanger/HeatExchangerPort.vue'
import { ComponentOrientation, HeatingState } from '@/modules/thrapp/mimics/components'
import { HeatExchangerPortOrientation } from '@/modules/thrapp/mimics/components/heat-exchanger'
</script>

<template>
  <HeatExchanger
    :state="HeatingState.HeatingMedium"
    :orientation="ComponentOrientation.Right"
  >
    <HeatExchangerPort
      side="a"
      :state="HeatingState.HeatingMedium"
      :orientation="HeatExchangerPortOrientation.Side"
    />
    <HeatExchangerPort
      side="b"
      :state="HeatingState.CoolingMedium"
      :orientation="HeatExchangerPortOrientation.Top"
    />
  </HeatExchanger>
</template>
```

## Semantic Token Mapping

| Element | State Input | Token Mapping |
|---|---|---|
| Shell stroke | `HeatingState.Idle` | `--attention-dull` |
| Shell stroke | Any non-idle `HeatingState` | `--attention` |
| Port zig-zag stroke | Port `state` | Matching `HEATING_STATE_COLORS` token |
| Port connector stroke | `HeatingState.Idle` | `--attention-dull` |
| Port connector stroke | Any non-idle `HeatingState` | `--attention` |
| Port connector fill | Always | `--background` |
