# TWS Selector

A select component for choosing True Wind Speed (TWS) ranges in knots.

<script setup>
import TWSSelector from '@/modules/loads/components/tws-selector/TWSSelector.vue'
import { ref } from 'vue'

const selectedTWS = ref(0)
</script>

## Overview

The TWSSelector component provides a dropdown interface for selecting predefined True Wind Speed ranges. It uses the Select component from shadcn-vue and displays speed ranges in knots (kts).

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <TWSSelector v-model="selectedTWS" />
</div>

```vue
<script setup>
import TWSSelector from '@/modules/loads/components/tws-selector/TWSSelector.vue'
import { ref } from 'vue'

const selectedTWS = ref(0)
</script>

<template>
  <TWSSelector v-model="selectedTWS" />
</template>
```

## Examples

### With Label

<div class="my-4 p-8 bg-muted">
  <div class="space-y-2">
    <label class="text-sm font-medium">Select Wind Speed</label>
    <TWSSelector v-model="selectedTWS" />
  </div>
</div>

```vue
<template>
  <div class="space-y-2">
    <label class="text-sm font-medium">Select Wind Speed</label>
    <TWSSelector v-model="selectedTWS" />
  </div>
</template>
```

### With Value Display

<div class="my-4 p-8 bg-muted">
  <div class="space-y-4">
    <TWSSelector v-model="selectedTWS" />
    <div class="text-sm text-muted-foreground">
      Selected range index: {{ selectedTWS }}
    </div>
  </div>
</div>

```vue
<template>
  <div class="space-y-4">
    <TWSSelector v-model="selectedTWS" />
    <div class="text-sm text-muted-foreground">
      Selected range index: {{ selectedTWS }}
    </div>
  </div>
</template>
```

## Available Ranges

The TWS selector provides the following predefined speed ranges:

- 0 - 5 kts
- 5 - 10 kts
- 10 - 15 kts
- 15 - 20 kts
- 20 - 25 kts
- 25 - 30 kts
- 30 - 40 kts
- 40 - 50 kts
- 50+ kts

These ranges are defined in the `TWS_VALUES` constant and represent common wind speed classifications used in sailing and marine operations.

## API Reference

### Props

The component uses `v-model` for two-way binding:

| Model | Type | Required | Description |
|-------|------|----------|-------------|
| `v-model` | `number` | Yes | The index of the selected TWS range (0-based) |

### Emits

| Event | Payload | Description |
|-------|---------|-------------|
| `update:modelValue` | `number` | Emitted when the selected range changes |

## Usage Guidelines

### When to Use

- Selecting wind speed ranges for sailing calculations
- Filtering data by wind speed categories
- Configuration interfaces for wind-related features
- Load calculation inputs based on wind strength
- Weather condition selection

### When Not to Use

- For precise wind speed input (use a number input instead)
- When continuous speed values are needed rather than ranges
- For non-wind-related speed selections

## Technical Details

- **Component Type**: Form input component
- **Based On**: shadcn-vue Select component
- **Value Type**: Index-based (0 to 9)
- **Unit**: Knots (kts)
- **Internationalization**: Uses `tScoped` for label localization
- **Special Case**: The last range (50+) represents "50 knots and above" using `Infinity` as the upper bound

## Accessibility

- Built on the accessible Select component from shadcn-vue
- Keyboard navigable (arrow keys, Enter, Escape)
- Screen reader friendly with proper ARIA attributes
- Supports focus management

## Related Components

- [TWA Selector](/components/twa-selector) - For selecting True Wind Angle ranges
- [Select](/components/select) - Base select component
