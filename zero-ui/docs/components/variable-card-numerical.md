# Load Card Numerical

A specialized card component for displaying numerical load values with threshold indicators and visual state representation.

<script setup>
import { VariableCardNumerical } from '@/modules/loads/components/variable-card-numerical'
import { VariableType } from '@/modules/loads/types'
</script>

## Overview

The VariableCardNumerical component displays a numerical value with visual indicators for target, warning, and destructive thresholds. The component automatically determines its visual state based on the current value and defined thresholds, using color coding to convey the load status.

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="0.8"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="0.8"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

## Examples

### Tonnes Load States

The following examples demonstrate the load card displaying values in tonnes with different states based on thresholds.

#### Below Target (Neutral)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="0.8"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="0.8"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

#### Above Target (Warning)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="2.5"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="2.5"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

#### Exceeding Destructive Threshold

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="3.1"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="3.1"
    :type="VariableType.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

### Percentage Load States

The following examples demonstrate the load card displaying percentage values with different states.

#### At Target (Neutral)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="10"
    :type="VariableType.Percentage"
    :thresholds="{
      target: 10,
      warningHigh: 15,
      alarmHigh: 28
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="10"
    :type="VariableType.Percentage"
    :thresholds="{
      target: 10,
      warningHigh: 15,
      alarmHigh: 28
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

#### Above Target (Warning)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="20"
    :type="VariableType.Percentage"
    :thresholds="{
      target: 10,
      warningHigh: 15,
      alarmHigh: 28
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="20"
    :type="VariableType.Percentage"
    :thresholds="{
      target: 10,
      warningHigh: 15,
      alarmHigh: 28
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

#### Exceeding Destructive Threshold

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCardNumerical
    :value="30"
    :type="VariableType.Percentage"
    :thresholds="{
      target: 10,
      warningHigh: 15,
      alarmHigh: 28
    }"
  >
    Push
  </VariableCardNumerical>
</div>

```vue
<template>
  <VariableCardNumerical
    :value="30"
    :type="VariableType.Percentage"
    :thresholds="{
      target: 10,
      warningHigh: 15,
      alarmHigh: 28
    }"
  >
    Push
  </VariableCardNumerical>
</template>
```

### All Six Examples in a Grid

<div class="my-4 p-8 bg-muted">
  <div class="grid grid-cols-3 gap-4">
    <VariableCardNumerical
      :value="0.8"
      :type="VariableType.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="2.5"
      :type="VariableType.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="3.1"
      :type="VariableType.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="10"
      :type="VariableType.Percentage"
      :thresholds="{
        target: 10,
        warningHigh: 15,
        alarmHigh: 28
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="20"
      :type="VariableType.Percentage"
      :thresholds="{
        target: 10,
        warningHigh: 15,
        alarmHigh: 28
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="30"
      :type="VariableType.Percentage"
      :thresholds="{
        target: 10,
        warningHigh: 15,
        alarmHigh: 28
      }"
    >
      Push
    </VariableCardNumerical>
  </div>
</div>

```vue
<template>
  <div class="grid grid-cols-3 gap-4">
    <VariableCardNumerical
      :value="0.8"
      :type="VariableType.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="2.5"
      :type="VariableType.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="3.1"
      :type="VariableType.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="10"
      :type="VariableType.Percentage"
      :thresholds="{
        target: 10,
        warningHigh: 15,
        alarmHigh: 28
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="20"
      :type="VariableType.Percentage"
      :thresholds="{
        target: 10,
        warningHigh: 15,
        alarmHigh: 28
      }"
    >
      Push
    </VariableCardNumerical>
    <VariableCardNumerical
      :value="30"
      :type="VariableType.Percentage"
      :thresholds="{
        target: 10,
        warningHigh: 15,
        alarmHigh: 28
      }"
    >
      Push
    </VariableCardNumerical>
  </div>
</template>
```

## API Reference

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `value` | `number` | Yes | The current load value to display |
| `type` | `VariableType` | Yes | The type of load - either `VariableType.Tonnes` or `VariableType.Percentage` |
| `thresholds` | `LoadThresholds` | No | Optional threshold values for target, warning, and destructive states |

### Slots

| Slot | Description |
|------|-------------|
| `default` | The title/label to display at the bottom of the card |

### LoadThresholds Type

```typescript
type LoadThresholds = {
  target?: number;          // Target value indicator
  warningLow?: number;      // Low warning threshold
  warningHigh?: number;     // High warning threshold
  alarmLow?: number;  // Low alarm threshold
  alarmHigh?: number; // High alarm threshold
}
```

### VariableType Enum

```typescript
enum VariableType {
  Percentage = "percentage",  // Display as percentage
  Tonnes = "tonnes"          // Display as tonnes with 1 decimal place
}
```

## Load States

The component automatically determines its visual state based on the current value and thresholds:

- **Neutral** - Value is within normal range (between target and warning thresholds)
- **Warning** - Value has exceeded warning threshold but is below destructive threshold
- **Destructive** - Value has exceeded the destructive threshold

The visual state affects the color and appearance of the main value display.

## Usage Guidelines

### When to Use

- Displaying real-time load measurements with clear threshold indicators
- Showing critical operational values that require monitoring
- Presenting numerical data where exceeding limits has safety implications
- Dashboard displays requiring quick visual status assessment

### When Not to Use

- For text-based content or labels
- When precise threshold monitoring is not required
- For displaying multiple related metrics (consider a table or chart instead)
- When the data doesn't have meaningful thresholds

## Layout Features

- **Target Box**: Shows the target value with a visual indicator line when a target threshold is defined
- **Main Value**: Large, prominent display of the current value with state-based coloring
- **Unit Label**: Automatically displays the appropriate unit (%, t) based on the load type
- **Title**: Displays the provided title/label below the main value
- **Threshold Indicators**: Shows alarmLow and alarmHigh values at the bottom for reference

## Accessibility

- The component uses semantic HTML structure
- Color coding is supplemented with numerical values for clarity
- Threshold values are always visible for reference
- Title slot provides context for screen readers

## Design Notes

- Values are formatted according to type: percentages show as integers, tonnes show with 1 decimal place
- The target box automatically hides when no target threshold is provided
- All threshold values are optional - the component gracefully handles partial threshold data
- State colors follow the established design system (neutral, warning, destructive)
