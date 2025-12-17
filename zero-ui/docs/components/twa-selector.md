# TWA Selector

A select component for choosing True Wind Angle (TWA) ranges in degrees.

<script setup>
import TWASelector from '@/modules/loads/components/twa-selector/TWASelector.vue'
import { ref } from 'vue'

const selectedTWA = ref(0)
</script>

## Overview

The TWASelector component provides a dropdown interface for selecting predefined True Wind Angle ranges. It uses the Select component from shadcn-vue and displays angle ranges in degrees.

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <TWASelector v-model="selectedTWA" />
</div>

```vue
<script setup>
import TWASelector from '@/modules/loads/components/twa-selector/TWASelector.vue'
import { ref } from 'vue'

const selectedTWA = ref(0)
</script>

<template>
  <TWASelector v-model="selectedTWA" />
</template>
```

## Examples

### With Label

<div class="my-4 p-8 bg-muted">
  <div class="space-y-2">
    <label class="text-sm font-medium">Select Wind Angle</label>
    <TWASelector v-model="selectedTWA" />
  </div>
</div>

```vue
<template>
  <div class="space-y-2">
    <label class="text-sm font-medium">Select Wind Angle</label>
    <TWASelector v-model="selectedTWA" />
  </div>
</template>
```

### With Value Display

<div class="my-4 p-8 bg-muted">
  <div class="space-y-4">
    <TWASelector v-model="selectedTWA" />
    <div class="text-sm text-muted-foreground">
      Selected range index: {{ selectedTWA }}
    </div>
  </div>
</div>

```vue
<template>
  <div class="space-y-4">
    <TWASelector v-model="selectedTWA" />
    <div class="text-sm text-muted-foreground">
      Selected range index: {{ selectedTWA }}
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

- [TWS Selector](/components/tws-selector) - For selecting True Wind Speed ranges
- [Select](/components/select) - Base select component
