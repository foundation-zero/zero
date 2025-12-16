# Position Card

A composable card component for displaying position values with visual threshold indicators using and slider representation.

<script setup>
import { 
  PositionCard,
  PositionCardReferenceTarget,
  PositionCardSlider,
  PositionCardValue,
  PositionCardTitle
} from '@/modules/loads/components/position-card'
import { InfoTooltip } from '@/modules/common/components/info-tooltip'
</script>

## Overview

The PositionCard is a composable component system that displays position values with visual indicators for target, warning, and alarm thresholds. Following the shadcn philosophy, the component is composed of separate sub-components that you can arrange and customize as needed.

The slider supports two types:
- **Symmetric**: Displays a centered slider with values ranging from negative to positive
- **Asymmetric**: Displays a left-aligned slider with values ranging from zero to positive

### Composition

The PositionCard system consists of:
- `PositionCard` - The main container that provides context
- `PositionCardReferenceTarget` - Displays the target reference value
- `PositionCardSlider` - The slider visualization
- `PositionCardValue` - The numerical value display
- `PositionCardTitle` - The title/label text

### Basic Example

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.42"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="0.42"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

## Examples

### Symmetric Slider

The symmetric slider displays values centered around zero, useful for bidirectional measurements like position adjustments or offset values.

#### Within Normal Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.42"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="0.42"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

#### Warning Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.47"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="0.47"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

#### Alarm Range (Negative)

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="-0.58"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="-0.58"
    :thresholds="{
      target: 0.40,
      warningLow: 0.35,
      warningHigh: 0.45,
      alarmLow: 0.20,
      alarmHigh: 0.50
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="symmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

### Asymmetric Slider

The asymmetric slider displays values from zero upward, suitable for unidirectional measurements like absolute positions or progress values.

#### Within Normal Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.71"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="0.71"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

#### Warning Range

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.80"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="0.80"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

#### Alarm Range (Low)

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.20"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</div>

```vue
<template>
  <PositionCard
    :value="0.20"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>Info if needed</PositionCardTitle>
  </PositionCard>
</template>
```

### With Info Tooltip

You can add contextual help using the InfoTooltip component inside the PositionCardTitle.

<div class="my-4 p-8 bg-background flex justify-center">
  <PositionCard
    :value="0.80"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>
      Mast Position
      <InfoTooltip>
        This shows the current mast position as a percentage. Target position is 70%, with warning thresholds at 65%-75%.
      </InfoTooltip>
    </PositionCardTitle>
  </PositionCard>
</div>

```vue
<script setup>
import { InfoTooltip } from '@/modules/common/components/info-tooltip'
</script>

<template>
  <PositionCard
    :value="0.80"
    :thresholds="{
      target: 0.70,
      warningLow: 0.65,
      warningHigh: 0.75,
      alarmLow: 0.50,
      alarmHigh: 0.90
    }"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider type="asymmetric" />
    <PositionCardValue />
    <PositionCardTitle>
      Mast Position
      <InfoTooltip>
        This shows the current mast position as a ratio (0-1). 
        Target position is 0.70, with warning thresholds at 0.65-0.75.
      </InfoTooltip>
    </PositionCardTitle>
  </PositionCard>
</template>
```

### All Six Examples in a Grid

<div class="my-4">
  <div class="grid grid-cols-2 gap-4">
    <PositionCard
      :value="0.42"
      :thresholds="{
        target: 0.40,
        warningLow: 0.35,
        warningHigh: 0.45,
        alarmLow: 0.20,
        alarmHigh: 0.50
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="symmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.47"
      :thresholds="{
        target: 0.40,
        warningLow: 0.35,
        warningHigh: 0.45,
        alarmLow: 0.20,
        alarmHigh: 0.50
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="symmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="-0.58"
      :thresholds="{
        target: 0.40,
        warningLow: 0.35,
        warningHigh: 0.45,
        alarmLow: 0.20,
        alarmHigh: 0.50
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="symmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.71"
      :thresholds="{
        target: 0.70,
        warningLow: 0.65,
        warningHigh: 0.75,
        alarmLow: 0.50,
        alarmHigh: 0.90
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.80"
      :thresholds="{
        target: 0.70,
        warningLow: 0.65,
        warningHigh: 0.75,
        alarmLow: 0.50,
        alarmHigh: 0.90
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.20"
      :thresholds="{
        target: 0.70,
        warningLow: 0.65,
        warningHigh: 0.75,
        alarmLow: 0.50,
        alarmHigh: 0.90
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
  </div>
</div>

```vue
<template>
  <div class="grid grid-cols-3 gap-4">
    <PositionCard
      :value="0.42"
      :thresholds="{
        target: 0.40,
        warningLow: 0.35,
        warningHigh: 0.45,
        alarmLow: 0.20,
        alarmHigh: 0.50
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="symmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.47"
      :thresholds="{
        target: 0.40,
        warningLow: 0.35,
        warningHigh: 0.45,
        alarmLow: 0.20,
        alarmHigh: 0.50
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="symmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="-0.58"
      :thresholds="{
        target: 0.40,
        warningLow: 0.35,
        warningHigh: 0.45,
        alarmLow: 0.20,
        alarmHigh: 0.50
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="symmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.71"
      :thresholds="{
        target: 0.70,
        warningLow: 0.65,
        warningHigh: 0.75,
        alarmLow: 0.50,
        alarmHigh: 0.90
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.80"
      :thresholds="{
        target: 0.70,
        warningLow: 0.65,
        warningHigh: 0.75,
        alarmLow: 0.50,
        alarmHigh: 0.90
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
    </PositionCard>
    <PositionCard
      :value="0.20"
      :thresholds="{
        target: 0.70,
        warningLow: 0.65,
        warningHigh: 0.75,
        alarmLow: 0.50,
        alarmHigh: 0.90
      }"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>Info if needed</PositionCardTitle>
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
- **Slider**: Visual representation of current position with threshold zones
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
