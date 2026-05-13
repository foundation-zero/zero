# Pump

Mimic pump component with four operational states: active, transient, closed, and alarm.

<script setup lang="ts">
import Pump from '@/modules/thrapp/mimics/components/pump/Pump.vue'
import { PumpState } from '@/modules/thrapp/mimics/components/pump'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`Pump` is a compact SVG-first mimic primitive derived directly from Figma geometry.

- `active` uses constructive accents to indicate normal operation
- `transient` highlights intermediate behavior with a warning blade color
- `closed` keeps the neutral body while marking the blade as destructive
- `alarm` applies a full destructive palette across the icon

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `state` | `PumpState` | `PumpState.Active` | Visual state of the pump (`active`, `transient`, `closed`, `alarm`) |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Right` | Required orientation for this pump instance in the mimic diagram |

## Orientation Logic

`Pump` follows the mimic orientation convention:

- `PUMP_BASE_ORIENTATION` represents the direction of the Figma drawing (`ComponentOrientation.Right`).
- `orientation` represents the required direction for this instance in your diagram.
- State variants (`transient`, `closed`) are derived from `orientation` by applying orientation steps, then mapped through `useOrientation`.

### Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Active" :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Active" :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Active" :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Active" :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

## States

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Active" />
    </div>
    <span class="text-sm font-mono">Active</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Transient" />
    </div>
    <span class="text-sm font-mono">Transient</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Closed" />
    </div>
    <span class="text-sm font-mono">Closed</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Pump :state="PumpState.Alarm" />
    </div>
    <span class="text-sm font-mono">Alarm</span>
  </div>
</div>

```vue
<script setup lang="ts">
import Pump from '@/modules/thrapp/mimics/components/pump/Pump.vue'
import { PumpState } from '@/modules/thrapp/mimics/components/pump'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

<template>
  <div class="flex gap-4">
    <Pump :state="PumpState.Active" :orientation="ComponentOrientation.Right" />
    <Pump :state="PumpState.Transient" :orientation="ComponentOrientation.Right" />
    <Pump :state="PumpState.Closed" :orientation="ComponentOrientation.Right" />
    <Pump :state="PumpState.Alarm" :orientation="ComponentOrientation.Right" />
  </div>
</template>
```

## Semantic Token Mapping

- `active`
  - ring: `--attention`
  - body: `--background`
  - blade: `--constructive-muted`
- `transient`
  - ring: `--attention`
  - body: `--background`
  - blade: `--warning`
- `closed`
  - ring: `--attention`
  - body: `--background`
  - blade: `--destructive-dull`
- `alarm`
  - ring: `--destructive`
  - body: `--destructive-dull`
  - blade: `--destructive-muted`