# Valve

A unified mimic valve component that supports switch, flow-control, and three-way variants.

<script setup lang="ts">
import { ref } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import Valve from '@/modules/thrapp/mimics/components/valve/Valve.vue'
import {
  ValveType,
  SwitchValveState,
  FlowValveState,
  ThreeWayValveState,
} from '@/modules/thrapp/mimics/components/valve'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'

const animatedSwitchState = ref(SwitchValveState.Open)

useIntervalFn(() => {
  animatedSwitchState.value =
    animatedSwitchState.value === SwitchValveState.Open
      ? SwitchValveState.Closed
      : SwitchValveState.Open
}, 1200)
</script>

## Overview

`Valve` combines switch, flow-control, and three-way valve types into one reusable component.

- `type="switch"` — renders two triangular ports with a circular labeled marker
- `type="flow-control"` — renders two triangular ports with a control-arrow marker
- `type="three-way"` — renders three triangular ports (left, right, bottom) with a control-arrow marker; each port is colored independently

State colors use semantic tokens:

- `open` → constructive (`--constructive-dull`)
- `partial` → warning (`--warning-dull`, flow-control only)
- `closed` → destructive (`--destructive-dull`)

For the three-way valve, each port's color reflects whether that specific port is open or closed for the given state.

## Examples

### Switch Valve States

<div class="grid grid-cols-2 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve
        :type="ValveType.Switch"
        :state="SwitchValveState.Open"
        :orientation="ComponentOrientation.Up"
        marker-label="A"
      />
    </div>
    <span class="text-sm font-mono">Open</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve
        :type="ValveType.Switch"
        :state="SwitchValveState.Closed"
        :orientation="ComponentOrientation.Up"
      />
    </div>
    <span class="text-sm font-mono">Closed</span>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <Valve
      :type="ValveType.Switch"
      :state="SwitchValveState.Open"
      :orientation="ComponentOrientation.Up"
      marker-label="A"
    />
    <Valve
      :type="ValveType.Switch"
      :state="SwitchValveState.Closed"
      :orientation="ComponentOrientation.Up"
    />
  </div>
</template>
```

### Switch Valve Animated Interval

This example toggles between open and closed every 1.2 seconds to show both transition effects:

- Rotation transition on the valve body
- Color transition between constructive and destructive states

<div class="my-6 flex flex-col items-center justify-center gap-3">
  <div class="rounded-md bg-muted p-4">
    <Valve
      :type="ValveType.Switch"
      :state="animatedSwitchState"
      :orientation="ComponentOrientation.Up"
      marker-label="A"
    />
  </div>
  <span class="text-sm font-mono">Current state: {{ animatedSwitchState }}</span>
</div>

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import Valve from '@/modules/thrapp/mimics/components/valve/Valve.vue'
import { ValveType, SwitchValveState } from '@/modules/thrapp/mimics/components/valve'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'

const switchState = ref(SwitchValveState.Open)

useIntervalFn(() => {
  switchState.value =
    switchState.value === SwitchValveState.Open
      ? SwitchValveState.Closed
      : SwitchValveState.Open
}, 1200)
</script>

<template>
  <Valve
    :type="ValveType.Switch"
    :state="switchState"
    :orientation="ComponentOrientation.Up"
    marker-label="A"
  />
</template>
```

### Flow-Control Valve States

<div class="grid grid-cols-3 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve
        :type="ValveType.FlowControl"
        :state="FlowValveState.Open"
        :orientation="ComponentOrientation.Up"
      />
    </div>
    <span class="text-sm font-mono">Open</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve
        :type="ValveType.FlowControl"
        :state="FlowValveState.Partial"
        :orientation="ComponentOrientation.Up"
      />
    </div>
    <span class="text-sm font-mono">Partial</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve
        :type="ValveType.FlowControl"
        :state="FlowValveState.Closed"
        :orientation="ComponentOrientation.Up"
      />
    </div>
    <span class="text-sm font-mono">Closed</span>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <Valve
      :type="ValveType.FlowControl"
      :state="FlowValveState.Open"
      :orientation="ComponentOrientation.Up"
    />
    <Valve
      :type="ValveType.FlowControl"
      :state="FlowValveState.Partial"
      :orientation="ComponentOrientation.Up"
    />
    <Valve
      :type="ValveType.FlowControl"
      :state="FlowValveState.Closed"
      :orientation="ComponentOrientation.Up"
    />
  </div>
</template>
```

### Flow-Control Orientations

<div class="grid grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.FlowControl" :state="FlowValveState.Open" :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.FlowControl" :state="FlowValveState.Open" :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.FlowControl" :state="FlowValveState.Open" :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.FlowControl" :state="FlowValveState.Open" :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

### Three-Way Valve States

<div class="grid grid-cols-5 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.Open" />
    </div>
    <span class="text-sm font-mono">Open</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.AA" />
    </div>
    <span class="text-sm font-mono">A-A</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.AB" />
    </div>
    <span class="text-sm font-mono">A-B</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.BA" />
    </div>
    <span class="text-sm font-mono">B-A</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.Closed" />
    </div>
    <span class="text-sm font-mono">Closed</span>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.Open" />
    <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.AA" />
    <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.AB" />
    <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.BA" />
    <Valve :type="ValveType.ThreeWay" :state="ThreeWayValveState.Closed" />
  </div>
</template>
```

State meanings for the three-way (T) valve:

| State | Left port | Right port | Bottom port |
|-------|-----------|------------|-------------|
| `Open` | open | open | open |
| `AA` | open | open | closed — left↔right flow |
| `AB` | open | closed | open — left↔bottom flow |
| `BA` | closed | open | open — right↔bottom flow |
| `Closed` | closed | closed | closed |

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| type | `ValveType` | - | Required valve variant (`Switch`, `FlowControl`, or `ThreeWay`) |
| state | `SwitchValveState \| FlowValveState \| ThreeWayValveState` | - | Required state for selected valve type |
| orientation | `ComponentOrientation` | `ComponentOrientation.Up` | Optional orientation used to rotate geometry |
| markerLabel | `string` | `'E'` | Optional marker text for switch valve only |

## Installation

```vue
<script setup lang="ts">
import Valve from '@/modules/thrapp/mimics/components/valve/Valve.vue'
import {
  ValveType,
  SwitchValveState,
  FlowValveState,
  ThreeWayValveState,
} from '@/modules/thrapp/mimics/components/valve'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

<template>
  <!-- Switch valve -->
  <Valve
    :type="ValveType.Switch"
    :state="SwitchValveState.Open"
    :orientation="ComponentOrientation.Up"
    marker-label="A"
  />

  <!-- Flow-control valve -->
  <Valve
    :type="ValveType.FlowControl"
    :state="FlowValveState.Partial"
    :orientation="ComponentOrientation.Right"
  />

  <!-- Three-way valve -->
  <Valve
    :type="ValveType.ThreeWay"
    :state="ThreeWayValveState.AB"
    :orientation="ComponentOrientation.Up"
  />
</template>
```

## Notes

- Single SVG output with no HTML wrapper elements.
- Uses semantic token colors only — no raw hex or rgb values.
- The three-way valve renders a T-shaped body (left, right, bottom ports); each port is colored independently based on the active state.
- The three-way valve does not shift orientation on `Closed` — unlike the switch and flow-control variants which rotate 90° when closed.
- Replaces the legacy switch-valve and flow-valve components with one unified API.
