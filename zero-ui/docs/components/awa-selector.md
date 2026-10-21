# AWA Selector

A select component for choosing Apparent Wind Angle (AWA) ranges in degrees.

<script setup>
import AWASelector from '@/modules/loads/components/awa-selector/AWASelector.vue'
import { ref } from 'vue'

const selectedAWA = ref('upwind')
</script>

## Overview

The AWASelector component provides a dropdown interface for selecting the Apparent Wind Angle range of a load case. It uses the Select component from shadcn-vue and shows each range by name.

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <AWASelector v-model="selectedAWA" />
</div>

```vue
<script setup>
import AWASelector from '@/modules/loads/components/awa-selector/AWASelector.vue'
import { ref } from 'vue'

const selectedAWA = ref('upwind')
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
      Selected range: {{ selectedAWA }}
    </div>
  </div>
</div>

```vue
<template>
  <div class="space-y-4">
    <AWASelector v-model="selectedAWA" />
    <div class="text-sm text-muted-foreground">
      Selected range: {{ selectedAWA }}
    </div>
  </div>
</template>
```

## Available Ranges

The AWA selector provides the following ranges:

- Upwind: 0 - 40°
- Reaching: 40 - 80°
- Downwind: 80 - 180°

These ranges are defined in the `AWA_VALUES` constant in `src/modules/loads/lib/consts.ts`. They must match `loads.awa_ranges` in the database and `AWA_RANGES` in the loads app's seed export.

## API Reference

### Props

The component uses `v-model` for two-way binding:

| Model | Type | Required | Description |
|-------|------|----------|-------------|
| `v-model` | `AWA` | Yes | The id of the selected AWA range (`upwind`, `reaching` or `downwind`) |

### Emits

| Event | Payload | Description |
|-------|---------|-------------|
| `update:modelValue` | `AWA` | Emitted when the selected range changes |

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
