# PVT String

Stateless mimic component representing a single PVT (photovoltaic-thermal) panel string.

<script setup lang="ts">
import PvtString from '@/modules/thrapp/mimics/components/pvt-string/PvtString.vue'
import { ComponentOrientation } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`PvtString` renders the exact Figma panel glyph: a bordered rectangular body with the internal wiring pattern. The default slot renders a label (typically the string number) inside the body.

The base orientation is `ComponentOrientation.Up`, matching the Figma drawing.

## Props

| Prop          | Type                   | Default                       | Description                                            |
| ------------- | ---------------------- | ------------------------------ | ------------------------------------------------------ |
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Up`      | Rotation of the string relative to its base orientation |
| `width`       | `number`               | `PVT_STRING_WIDTH` (`30`)      | SVG viewport width                                      |
| `height`      | `number`               | `PVT_STRING_HEIGHT` (`54`)     | SVG viewport height                                     |
| `state`       | `MimicComponentState`  | `MimicComponentState.Normal`   | Inherited mimic state; `PvtString` has no visual state mapping |

## Orientation Examples

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PvtString :orientation="ComponentOrientation.Up">1.1</PvtString>
    </div>
    <span class="text-sm font-mono">Up (base)</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PvtString :orientation="ComponentOrientation.Right">1.1</PvtString>
    </div>
    <span class="text-sm font-mono">Right</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PvtString :orientation="ComponentOrientation.Down">1.1</PvtString>
    </div>
    <span class="text-sm font-mono">Down</span>
  </div>
  <div class="flex flex-col items-center justify-center gap-2">
    <div class="p-4 bg-muted rounded-md">
      <PvtString :orientation="ComponentOrientation.Left">1.1</PvtString>
    </div>
    <span class="text-sm font-mono">Left</span>
  </div>
</div>

```vue
<script setup lang="ts">
import PvtString from "@/modules/thrapp/mimics/components/pvt-string/PvtString.vue";
import { ComponentOrientation } from "@/modules/thrapp/mimics/components";
</script>

<template>
  <div class="flex gap-4">
    <PvtString :orientation="ComponentOrientation.Up">1.1</PvtString>
    <PvtString :orientation="ComponentOrientation.Right">1.1</PvtString>
    <PvtString :orientation="ComponentOrientation.Down">1.1</PvtString>
    <PvtString :orientation="ComponentOrientation.Left">1.1</PvtString>
  </div>
</template>
```