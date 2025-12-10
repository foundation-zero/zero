# Position Card

A specialized card component for displaying position values with visual threshold indicators using an interactive slider representation.

<script setup>
import { PositionCard } from '@/modules/loads/components/position-card'
</script>

## Overview

The PositionCard component displays a position value with visual indicators for target, warning, and alarm thresholds. It features an interactive slider that visually represents the current value position relative to defined thresholds, using color coding to convey the state.

The component supports two slider types:
- **Symmetric**: Displays a centered slider with values ranging from negative to positive
- **Asymmetric**: Displays a left-aligned slider with values ranging from zero to positive

### Basic Example

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="42"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="42"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

## Examples

### Symmetric Slider

The symmetric slider displays values centered around zero, useful for bidirectional measurements like position adjustments or offset values.

#### Within Normal Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="42"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="42"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

#### Warning Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="47"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="47"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

#### Alarm Range (Negative)

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="-58"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="-58"
    :type="'symmetric'"
    :thresholds="{
      target: 40,
      warningLow: 35,
      warningHigh: 45,
      alarmLow: 20,
      alarmHigh: 50
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

### Asymmetric Slider

The asymmetric slider displays values from zero upward, suitable for unidirectional measurements like absolute positions or progress values.

#### Within Normal Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="71"
    :type="'asymmetric'"
    :thresholds="{
      target: 70,
      warningLow: 65,
      warningHigh: 75,
      alarmLow: 50,
      alarmHigh: 90
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="71"
    :type="'asymmetric'"
    :thresholds="{
      target: 70,
      warningLow: 65,
      warningHigh: 75,
      alarmLow: 50,
      alarmHigh: 90
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

#### Warning Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="80"
    :type="'asymmetric'"
    :thresholds="{
      target: 70,
      warningLow: 65,
      warningHigh: 75,
      alarmLow: 50,
      alarmHigh: 90
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="80"
    :type="'asymmetric'"
    :thresholds="{
      target: 70,
      warningLow: 65,
      warningHigh: 75,
      alarmLow: 50,
      alarmHigh: 90
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

#### Alarm Range (Low)

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="20"
    :type="'asymmetric'"
    :thresholds="{
      target: 70,
      warningLow: 65,
      warningHigh: 75,
      alarmLow: 50,
      alarmHigh: 90
    }"
  >
    Info if needed
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="20"
    :type="'asymmetric'"
    :thresholds="{
      target: 70,
      warningLow: 65,
      warningHigh: 75,
      alarmLow: 50,
      alarmHigh: 90
    }"
  >
    Info if needed
  </PositionCard>
</template>
```

### All Six Examples in a Grid

<div class="my-4">
  <div class="grid grid-cols-2 gap-4">
    <PositionCard
      :value="42"
      :type="'symmetric'"
      :thresholds="{
        target: 40,
        warningLow: 35,
        warningHigh: 45,
        alarmLow: 20,
        alarmHigh: 50
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="47"
      :type="'symmetric'"
      :thresholds="{
        target: 40,
        warningLow: 35,
        warningHigh: 45,
        alarmLow: 20,
        alarmHigh: 50
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="-58"
      :type="'symmetric'"
      :thresholds="{
        target: 40,
        warningLow: 35,
        warningHigh: 45,
        alarmLow: 20,
        alarmHigh: 50
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="71"
      :type="'asymmetric'"
      :thresholds="{
        target: 70,
        warningLow: 65,
        warningHigh: 75,
        alarmLow: 50,
        alarmHigh: 90
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="80"
      :type="'asymmetric'"
      :thresholds="{
        target: 70,
        warningLow: 65,
        warningHigh: 75,
        alarmLow: 50,
        alarmHigh: 90
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="20"
      :type="'asymmetric'"
      :thresholds="{
        target: 70,
        warningLow: 65,
        warningHigh: 75,
        alarmLow: 50,
        alarmHigh: 90
      }"
    >
      Info if needed
    </PositionCard>
  </div>
</div>

```vue
<template>
  <div class="grid grid-cols-3 gap-4">
    <PositionCard
      :value="42"
      :type="'symmetric'"
      :thresholds="{
        target: 40,
        warningLow: 35,
        warningHigh: 45,
        alarmLow: 20,
        alarmHigh: 50
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="47"
      :type="'symmetric'"
      :thresholds="{
        target: 40,
        warningLow: 35,
        warningHigh: 45,
        alarmLow: 20,
        alarmHigh: 50
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="-58"
      :type="'symmetric'"
      :thresholds="{
        target: 40,
        warningLow: 35,
        warningHigh: 45,
        alarmLow: 20,
        alarmHigh: 50
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="71"
      :type="'asymmetric'"
      :thresholds="{
        target: 70,
        warningLow: 65,
        warningHigh: 75,
        alarmLow: 50,
        alarmHigh: 90
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="80"
      :type="'asymmetric'"
      :thresholds="{
        target: 70,
        warningLow: 65,
        warningHigh: 75,
        alarmLow: 50,
        alarmHigh: 90
      }"
    >
      Info if needed
    </PositionCard>
    <PositionCard
      :value="20"
      :type="'asymmetric'"
      :thresholds="{
        target: 70,
        warningLow: 65,
        warningHigh: 75,
        alarmLow: 50,
        alarmHigh: 90
      }"
    >
      Info if needed
    </PositionCard>
  </div>
</template>
```

## API Reference

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `value` | `number` | Yes | The current position value to display |
| `type` | `SliderType` | Yes | The slider type - either `'symmetric'` or `'asymmetric'` |
| `thresholds` | `ReferenceThresholds` | No | Optional threshold values for target, warning, and alarm states |

### Slots

| Slot | Description |
|------|-------------|
| `default` | The title/label to display at the bottom of the card |

### ReferenceThresholds Type

```typescript
type ReferenceThresholds = {
  target: number;        // Target value indicator
  warningLow: number;    // Low warning threshold
  warningHigh: number;   // High warning threshold
  alarmLow: number;      // Low alarm threshold
  alarmHigh: number;     // High alarm threshold
}
```

### SliderType

```typescript
type SliderType = 'symmetric' | 'asymmetric'
```

- **symmetric**: Displays a centered slider with negative and positive values
- **asymmetric**: Displays a left-aligned slider starting from zero

## State Determination

The component automatically determines its visual state based on the current value and thresholds:

- **Neutral** - Value is within normal range (between warning thresholds)
- **Warning** - Value has exceeded warning threshold but is within alarm threshold
- **Alarm** - Value has exceeded the alarm threshold

The visual state affects the color of the slider position indicator and the main value display.

## Usage Guidelines

### When to Use

- Displaying position measurements with threshold monitoring
- Showing adjustable values that need visual reference points
- Presenting bidirectional or unidirectional position data
- Dashboard displays requiring quick visual assessment of position status

### When Not to Use

- For simple numerical displays without threshold monitoring (use LoadCardNumerical instead)
- For boolean or discrete state indicators (use IndicatorLight instead)
- For text-based content or labels (use Badge instead)
- When precise numerical values are more important than visual position

### Choosing Slider Type

- **Use symmetric** for:
  - Position adjustments relative to center
  - Offset or deviation measurements
  - Bidirectional position values
  - Values that naturally range negative to positive

- **Use asymmetric** for:
  - Absolute position measurements
  - Unidirectional progress indicators
  - Percentage values
  - Values that start from zero

## Layout Features

- **Reference Box**: Shows the target value with a visual indicator when a target threshold is defined
- **Interactive Slider**: Visual representation of current position with threshold zones
- **Main Value**: Large, prominent display of the current value with state-based coloring
- **Unit Label**: Automatically displays percentage symbol (%)
- **Title**: Displays the provided title/label below the main value

## Accessibility

- The component uses semantic HTML structure
- Color coding is supplemented with numerical values for clarity
- Threshold zones are visually distinct on the slider
- Title slot provides context for screen readers

## Design Notes

- Values are always displayed as percentages with integer formatting
- The reference box automatically hides when no target threshold is provided
- All threshold values are optional - the component gracefully handles partial threshold data
- State colors follow the established design system (neutral, warning, alarm)
- Slider visual representation adapts based on the selected type (symmetric/asymmetric)
