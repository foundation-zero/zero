# Manual Valve

A stateless directional manual valve mimic component for use in THRAPP diagrams.

<script setup lang="ts">
import ManualValve from '@/modules/thrapp/mimics/components/manual-valve/ManualValve.vue'
import { ManualValveType } from '@/modules/thrapp/mimics/components/manual-valve'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

The shape mirrors the [Actuated Valve](/mimics/actuated-valve) body but uses a manual control marker instead of a motorised actuator. There is no state prop — the valve displays its type and orientation only.

## Types

### Switch Valve

The switch variant uses a circular pivot and center dot.

<div class="flex gap-4 my-6 items-center justify-center">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.Switch" />
    </div>
    <span class="text-sm font-mono">Switch</span>
  </div>
</div>

### Flow-Control Valve

The flow-control variant uses a diagonal arrow marker to indicate adjustable flow.

<div class="flex gap-4 my-6 items-center justify-center">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.FlowControl" />
    </div>
    <span class="text-sm font-mono">FlowControl</span>
  </div>
</div>

### Three-Way Valve

The three-way variant adds a bottom port triangle with the same pivot marker.

<div class="flex gap-4 my-6 items-center justify-center">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.ThreeWay" />
    </div>
    <span class="text-sm font-mono">ThreeWay</span>
  </div>
</div>

```vue
<template>
  <ManualValve :type="ManualValveType.Switch" />
  <ManualValve :type="ManualValveType.FlowControl" />
  <ManualValve :type="ManualValveType.ThreeWay" />
</template>
```

### Manual Flow Valve

The `Flow` variant uses the exact Figma `Man-flow` marker: a circular pivot with a stroked adjustment arrow. The marker stays upright while the port body rotates. The existing `FlowControl` variant retains its original filled arrow and rotation behavior.

<div class="flex gap-4 my-6 items-center justify-center">
  <ManualValve :type="ManualValveType.Flow" />
  <ManualValve :type="ManualValveType.Flow" :orientation="ComponentOrientation.Right" />
</div>

```vue
<ManualValve :type="ManualValveType.Flow" :orientation="ComponentOrientation.Right" />
```

## Composition

Like `ActuatedValve`, `ManualValve` supports SVG composition. The default slot replaces the port body; the `marker` slot replaces the marker. Omitted slots retain the geometry selected by `type`.

```vue
<script setup lang="ts">
import ManualValve from "@/modules/thrapp/mimics/components/manual-valve/ManualValve.vue";
import { ManualFlowMarker } from "@/modules/thrapp/mimics/components/manual-valve";
</script>

<template>
  <ManualValve>
    <template #marker>
      <ManualFlowMarker />
    </template>
  </ManualValve>
</template>
```

## Orientations

All types support the `orientation` prop. The valve body and legacy markers rotate together around the icon center; the `Flow` marker counter-rotates to remain upright. `Up` is the horizontal port layout and `Right` is vertical.

<div class="grid grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.Switch" :orientation="ComponentOrientation.Up" />
    </div>
    <span class="text-sm font-mono">Up</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.Switch" :orientation="ComponentOrientation.Right" />
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.Switch" :orientation="ComponentOrientation.Down" />
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <ManualValve :type="ManualValveType.Switch" :orientation="ComponentOrientation.Left" />
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

```vue
<template>
  <ManualValve
    :type="ManualValveType.Switch"
    :orientation="ComponentOrientation.Up"
  />
  <ManualValve
    :type="ManualValveType.Switch"
    :orientation="ComponentOrientation.Right"
  />
  <ManualValve
    :type="ManualValveType.Switch"
    :orientation="ComponentOrientation.Down"
  />
  <ManualValve
    :type="ManualValveType.Switch"
    :orientation="ComponentOrientation.Left"
  />
</template>
```

## Props

| Prop          | Type                   | Default                   | Description                                                             |
| ------------- | ---------------------- | ------------------------- | ----------------------------------------------------------------------- |
| `type`        | `ManualValveType`      | `ManualValveType.Switch`  | Switch, legacy flow-control, manual flow, or three-way fallback variant |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Up` | Rotation of the valve relative to its base orientation                  |

## Semantic Token Mapping

| Element                               | Token                |
| ------------------------------------- | -------------------- |
| Port triangle fill                    | `var(--background)`  |
| Port triangle stroke                  | `var(--brand-muted)` |
| Switch / ThreeWay pivot circle stroke | `var(--brand-muted)` |
| Switch / ThreeWay inner dot fill      | `var(--foreground)`  |
| FlowControl pivot circle stroke       | `var(--brand-muted)` |
| FlowControl arrow fill                | `var(--foreground)`  |
| Flow pivot circle stroke              | `var(--brand-muted)` |
| Flow arrow fill and stroke            | `var(--foreground)`  |
