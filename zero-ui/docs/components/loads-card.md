# Loads Card

A specialized card component for displaying load values with visual indicators showing the current state relative to target and warning/alarm thresholds.

<script setup>
import { LoadsCard } from '@/modules/loads/components/loads-card'
import { VariableUnit } from '@/modules/loads/types'
</script>

## Overview

The Loads Card component provides a visual gauge interface for monitoring load values. It displays:
- A semicircular gauge with animated dots representing the value range
- Color-coded indicators (green/yellow/red) based on threshold states
- Target value display with reference box
- Current value display with unit and state

The gauge supports both symmetric and asymmetric scales, and automatically adapts its visual representation based on the target position and threshold configuration.

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `value` | `number \| undefined` | No | Current load value to display |
| `thresholds` | `ReferenceThresholds` | Yes | Object defining target, warning, and alarm thresholds |
| `scale` | `[number, number]` | Yes | Min and max values for the gauge scale |
| `class` | `string` | No | Additional CSS classes |

### ReferenceThresholds Type

```typescript
type ReferenceThresholds = {
  target: number;          // Target value (displayed at top of gauge)
  warningLow?: number;     // Lower warning threshold
  warningHigh?: number;    // Upper warning threshold
  alarmLow?: number;       // Lower alarm threshold
  alarmHigh?: number;      // Upper alarm threshold
}
```

## Color States

- **Constructive (Green)**: Value is within warning thresholds
- **Warning (Yellow)**: Value is outside warning thresholds but within alarm thresholds
- **Destructive (Red)**: Value is outside alarm thresholds

## Examples

### Symmetric Scale - Value in Target Range

A balanced scale centered around the target value with the current value within the target range.

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="0.5"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="0.5"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
  />
</template>
```

### Symmetric Scale - Value in Warning Range

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="1.5"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="1.5"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
  />
</template>
```

### Symmetric Scale - Value in Alarm Range

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="-2.5"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="-2.5"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
  />
</template>
```

### Asymmetric Scale - Target at 0

An asymmetric scale where the target is at 0, but the range extends further in the positive direction.

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="2"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -3,
      alarmHigh: 3
    }"
    :scale="[-3, 5]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="2"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -3,
      alarmHigh: 3
    }"
    :scale="[-3, 5]"
  />
</template>
```

### Asymmetric Scale - Negative Value

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="-2"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -3,
      alarmHigh: 3
    }"
    :scale="[-3, 5]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="-2"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -3,
      alarmHigh: 3
    }"
    :scale="[-3, 5]"
  />
</template>
```

### Without Warning Range - Only Alarm Thresholds

Display with only alarm thresholds defined (warning thresholds omitted).

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="3"
    :thresholds="{
      target: 0,
      alarmLow: -4,
      alarmHigh: 4
    }"
    :scale="[-5, 5]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="3"
    :thresholds="{
      target: 0,
      alarmLow: -4,
      alarmHigh: 4
    }"
    :scale="[-5, 5]"
  />
</template>
```

### Without Any Thresholds - Target Only

Display with only a target value and no warning or alarm ranges.

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="2"
    :thresholds="{
      target: 0
    }"
    :scale="[-3, 5]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="2"
    :thresholds="{
      target: 0
    }"
    :scale="[-3, 5]"
  />
</template>
```

### Off-Center Target

A scale where the target is not centered.

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="5"
    :thresholds="{
      target: 2,
      warningLow: 1,
      warningHigh: 3,
      alarmLow: -1,
      alarmHigh: 5
    }"
    :scale="[-2, 8]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="5"
    :thresholds="{
      target: 2,
      warningLow: 1,
      warningHigh: 3,
      alarmLow: -1,
      alarmHigh: 5
    }"
    :scale="[-2, 8]"
  />
</template>
```

### Undefined Value

Display when no current value is available.

<div class="my-4 p-4 bg-muted">
  <LoadsCard
    :value="undefined"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
    class="mx-auto"
  />
</div>

```vue
<template>
  <LoadsCard
    :value="undefined"
    :thresholds="{
      target: 0,
      warningLow: -1,
      warningHigh: 1,
      alarmLow: -2,
      alarmHigh: 2
    }"
    :scale="[-3, 3]"
  />
</template>
```

## Behavior

### Animation

The gauge circles animate sequentially when the value changes:
- **Increasing values**: circles fill from the center (target) outward
- **Decreasing values**: circles empty from the furthest point back to center
- Animation duration is 300ms by default
- Smooth color transitions using CSS

### Responsive Layout

The card has a fixed height of 13.375rem (214px) with a minimum width of 11em, making it suitable for grid layouts.

### State Calculation

The component automatically determines the visual state based on the current value:
1. **Unknown**: When value is undefined
2. **Neutral**: Within warning thresholds (or entire scale if no thresholds)
3. **Warning**: Outside warning but within alarm thresholds
4. **Alarm**: Outside alarm thresholds

## Accessibility

- Uses semantic SVG elements for the gauge
- Color coding is supplemented with value display
- State information is clearly indicated through both color and text
