# AWA Selector

A select component for choosing Apparent Wind Angle (AWA) ranges in degrees.

<script setup>
import AWASelector from '@/modules/loads/components/awa-selector/AWASelector.vue'
import { ref } from 'vue'

const selectedAWA = ref(0)
</script>

## Overview

The AWASelector component provides a dropdown interface for selecting predefined True Wind Angle ranges. It uses the Select component from shadcn-vue and displays angle ranges in degrees.

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <AWASelector v-model="selectedAWA" />
</div>

```vue
<script setup>
import AWASelector from '@/modules/loads/components/awa-selector/AWASelector.vue'
import { ref } from 'vue'

const selectedAWA = ref(0)
</script>

<template>
  <AWASelector v-model="selectedAWA" />
</template>
```

## Examples

### With Label

<div class="my-4 p-8 bg-muted">
  <div class="space-y-2">
    <label class="text-sm font-medium">Select Wind Angle</label>
    <AWASelector v-model="selectedAWA" />
  </div>
</div>

```vue
<template>
  <div class="space-y-2">
    <label class="text-sm font-medium">Select Wind Angle</label>
    <AWASelector v-model="selectedAWA" />
  </div>
</template>
```

### With Value Display

<div class="my-4 p-8 bg-muted">
  <div class="space-y-4">
    <AWASelector v-model="selectedAWA" />
    <div class="text-sm text-muted-foreground">
      Selected range index: {{ selectedAWA }}
    </div>
  </div>
</div>

```vue
<template>
  <div class="space-y-4">
    <AWASelector v-model="selectedAWA" />
    <div class="text-sm text-muted-foreground">
      Selected range index: {{ selectedAWA }}
    </div>
  </div>
</template>
```

## Available Ranges

The TWA selector provides the following predefined angle ranges:

- 0 - 40°
- 40 - 50°
- 50 - 60°
- 60 - 90°
- 90 - 120°
- 120 - 150°

These ranges are defined in the `TWA_VALUES` constant and represent common sailing wind angle classifications.

## API Reference

### Props

The component uses `v-model` for two-way binding:

| Model | Type | Required | Description |
|-------|------|----------|-------------|
| `v-model` | `number` | Yes | The index of the selected TWA range (0-based) |

### Emits

| Event | Payload | Description |
|-------|---------|-------------|
| `update:modelValue` | `number` | Emitted when the selected range changes |

## Usage Guidelines

### When to Use

- Selecting wind angle ranges for sailing calculations
- Filtering data by wind angle categories
- Configuration interfaces for wind-related features
- Load calculation inputs based on wind direction

### When Not to Use

- For precise angle input (use a number input or slider instead)
- When continuous angle values are needed rather than ranges
- For non-wind-related angle selections

## Technical Details

- **Component Type**: Form input component
- **Based On**: shadcn-vue Select component
- **Value Type**: Index-based (0 to 5)
- **Internationalization**: Uses `tScoped` for label localization

## Accessibility

- Built on the accessible Select component from shadcn-vue
- Keyboard navigable (arrow keys, Enter, Escape)
- Screen reader friendly with proper ARIA attributes
- Supports focus management

## Related Components

- [AWS Selector](/components/aws-selector) - For selecting True Wind Speed ranges
- [Select](/components/select) - Base select component
