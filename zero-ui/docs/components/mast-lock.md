# Mast Lock

A specialized component for displaying mast lock status with two independent indicator states: locked and overhoist positions.

<script setup>
import { MastLock } from '@/modules/loads/components/mast-lock'
</script>

## Overview

The MastLock component provides a visual representation of mast lock status with two independent indicator lights showing locked and overhoist conditions. Each indicator uses the same variants as IndicatorLight (neutral, constructive, destructive) to convey different status states.

### Default State

<div class="my-4 p-8 bg-background flex justify-center">
  <MastLock>R1</MastLock>
</div>

```vue
<template>
  <MastLock>R1</MastLock>
</template>
```

## Examples

### All Neutral (Inactive)

All indicators in neutral state, showing no active conditions.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock>R1</MastLock>
    <MastLock>R2</MastLock>
    <MastLock>R3</MastLock>
    <MastLock>Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock>R1</MastLock>
    <MastLock>R2</MastLock>
    <MastLock>R3</MastLock>
    <MastLock>Full</MastLock>
  </div>
</template>
```

### Locked - Constructive State

Showing locked condition with constructive (green) indicator.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock locked="constructive">R1</MastLock>
    <MastLock locked="constructive">R2</MastLock>
    <MastLock locked="constructive">R3</MastLock>
    <MastLock locked="constructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock locked="constructive">R1</MastLock>
    <MastLock locked="constructive">R2</MastLock>
    <MastLock locked="constructive">R3</MastLock>
    <MastLock locked="constructive">Full</MastLock>
  </div>
</template>
```

### Locked - Destructive State

Showing locked condition with destructive (red) indicator, typically for error states.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock locked="destructive">R1</MastLock>
    <MastLock locked="destructive">R2</MastLock>
    <MastLock locked="destructive">R3</MastLock>
    <MastLock locked="destructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock locked="destructive">R1</MastLock>
    <MastLock locked="destructive">R2</MastLock>
    <MastLock locked="destructive">R3</MastLock>
    <MastLock locked="destructive">Full</MastLock>
  </div>
</template>
```

### Overhoist - Constructive State

Showing overhoist condition with constructive (green) indicator.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock overhoist="constructive">R1</MastLock>
    <MastLock overhoist="constructive">R2</MastLock>
    <MastLock overhoist="constructive">R3</MastLock>
    <MastLock overhoist="constructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock overhoist="constructive">R1</MastLock>
    <MastLock overhoist="constructive">R2</MastLock>
    <MastLock overhoist="constructive">R3</MastLock>
    <MastLock overhoist="constructive">Full</MastLock>
  </div>
</template>
```

### Overhoist - Destructive State

Showing overhoist condition with destructive (red) indicator, typically for warning states.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock overhoist="destructive">R1</MastLock>
    <MastLock overhoist="destructive">R2</MastLock>
    <MastLock overhoist="destructive">R3</MastLock>
    <MastLock overhoist="destructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock overhoist="destructive">R1</MastLock>
    <MastLock overhoist="destructive">R2</MastLock>
    <MastLock overhoist="destructive">R3</MastLock>
    <MastLock overhoist="destructive">Full</MastLock>
  </div>
</template>
```

### Both Locked and Overhoist - Constructive

Both conditions active with constructive indicators.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock locked="constructive" overhoist="constructive">R1</MastLock>
    <MastLock locked="constructive" overhoist="constructive">R2</MastLock>
    <MastLock locked="constructive" overhoist="constructive">R3</MastLock>
    <MastLock locked="constructive" overhoist="constructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock locked="constructive" overhoist="constructive">R1</MastLock>
    <MastLock locked="constructive" overhoist="constructive">R2</MastLock>
    <MastLock locked="constructive" overhoist="constructive">R3</MastLock>
    <MastLock locked="constructive" overhoist="constructive">Full</MastLock>
  </div>
</template>
```

### Both Locked and Overhoist - Destructive

Both conditions active with destructive indicators.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock locked="destructive" overhoist="destructive">R1</MastLock>
    <MastLock locked="destructive" overhoist="destructive">R2</MastLock>
    <MastLock locked="destructive" overhoist="destructive">R3</MastLock>
    <MastLock locked="destructive" overhoist="destructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock locked="destructive" overhoist="destructive">R1</MastLock>
    <MastLock locked="destructive" overhoist="destructive">R2</MastLock>
    <MastLock locked="destructive" overhoist="destructive">R3</MastLock>
    <MastLock locked="destructive" overhoist="destructive">Full</MastLock>
  </div>
</template>
```

### Mixed States

Different combinations of locked and overhoist states.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <MastLock locked="constructive" overhoist="neutral">R1</MastLock>
    <MastLock locked="neutral" overhoist="destructive">R2</MastLock>
    <MastLock locked="constructive" overhoist="destructive">R3</MastLock>
    <MastLock locked="destructive" overhoist="constructive">Full</MastLock>
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <MastLock locked="constructive" overhoist="neutral">R1</MastLock>
    <MastLock locked="neutral" overhoist="destructive">R2</MastLock>
    <MastLock locked="constructive" overhoist="destructive">R3</MastLock>
    <MastLock locked="destructive" overhoist="constructive">Full</MastLock>
  </div>
</template>
```

### All Variations Grid

Comprehensive display of all possible state combinations for a single mast.

<div class="my-4 p-8 bg-background">
  <div class="grid grid-cols-3 gap-4 max-w-md mx-auto">
    <div class="flex flex-col items-center gap-2">
      <MastLock>R1</MastLock>
      <span class="text-xs text-muted-foreground">All Neutral</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock locked="constructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Locked</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock locked="destructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Locked Error</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock overhoist="constructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Overhoist</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock overhoist="destructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Overhoist Warn</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock locked="constructive" overhoist="constructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Both Active</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock locked="destructive" overhoist="destructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Both Error</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock locked="constructive" overhoist="destructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Mixed 1</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <MastLock locked="destructive" overhoist="constructive">R1</MastLock>
      <span class="text-xs text-muted-foreground">Mixed 2</span>
    </div>
  </div>
</div>

```vue
<template>
  <div class="grid grid-cols-3 gap-4">
    <MastLock>R1</MastLock>
    <MastLock locked="constructive">R1</MastLock>
    <MastLock locked="destructive">R1</MastLock>
    <MastLock overhoist="constructive">R1</MastLock>
    <MastLock overhoist="destructive">R1</MastLock>
    <MastLock locked="constructive" overhoist="constructive">R1</MastLock>
    <MastLock locked="destructive" overhoist="destructive">R1</MastLock>
    <MastLock locked="constructive" overhoist="destructive">R1</MastLock>
    <MastLock locked="destructive" overhoist="constructive">R1</MastLock>
  </div>
</template>
```

## API Reference

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `locked` | `'neutral' \| 'constructive' \| 'destructive'` | `'neutral'` | Status variant for the locked indicator |
| `overhoist` | `'neutral' \| 'constructive' \| 'destructive'` | `'neutral'` | Status variant for the overhoist indicator |
| `class` | `string` | - | Additional CSS classes for the container |

### Slots

| Slot | Description |
|------|-------------|
| default | Label text for the mast (e.g., "R1", "R2", "R3", "Full") |

## Indicator States

### neutral
Default inactive state with no glow, indicating the condition is not present.

### constructive
Active state with green glow, indicating:
- Locked condition is engaged
- Overhoist position is reached
- Normal operational status

### destructive
Error or warning state with red glow, indicating:
- Locked condition error
- Overhoist position warning
- Fault or critical condition

## Usage Guidelines

### When to Use

- **Mast Control Panels**: Display lock and overhoist status for crane masts
- **Safety Monitoring**: Show critical safety interlocks and position limits
- **Status Displays**: Provide real-time feedback on mast positions
- **Control Stations**: Monitor multiple mast segments simultaneously

### When Not to Use

- **Non-Mast Components**: Use other indicator components for general status
- **Detailed Information**: Use tables or detailed views for diagnostic data
- **Interactive Controls**: Use buttons or switches for user actions
- **Single Indicators**: Use IndicatorLight for simple status displays

## Label Conventions

Common label patterns for mast segments:

- **R1, R2, R3**: Individual reef positions (first, second, third)
- **Full**: Full mast extension or final position
- Custom labels can be provided through the default slot

## Accessibility

- Each indicator position includes text labels ("Locked", "Overhoist")
- Mast label is displayed below the indicators
- Consider providing additional context in surrounding UI
- Screen readers will announce the text content of all labels
- Color should not be the only means of conveying status

## Design Notes

The component features:
- Vertical layout with two indicator positions
- Fixed dimensions (24 units wide, 60 units high)
- Border with subtle styling for panel integration
- Stacked arrangement: Locked (top), Overhoist (middle), Label (bottom)
- Inherits IndicatorLight visual styling for status indicators
- Consistent spacing and alignment for multiple mast displays
