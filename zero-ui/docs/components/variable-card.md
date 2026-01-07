# Variable Card

A composable card component for displaying numerical variable values with threshold indicators and visual state representation.

<script setup>
import { 
  VariableCard,
  VariableCardReferenceTarget,
  VariableCardReferenceThresholds,
  VariableCardValue,
  VariableCardTitle
} from '@/modules/loads/components/variable-card'
import { VariableUnit } from '@/modules/loads/types'
import { ReferenceBoxLine } from '@/modules/loads/components/reference-box'
import { InfoTooltip } from '@/modules/common/components/info-tooltip'
</script>

## Overview

The VariableCard is a composable component system that displays numerical values with visual indicators for target, warning, and alarm thresholds. Following the shadcn philosophy, the component is composed of separate sub-components that you can arrange and customize as needed.

### Composition

The VariableCard system consists of:
- `VariableCard` - The main container that provides context
- `VariableCardReferenceTarget` - Displays the target reference value
- `VariableCardReferenceThresholds` - Displays the alarm threshold indicators
- `VariableCardValue` - The numerical value display with state-based styling
- `VariableCardTitle` - The title/label text

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="0.8"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="0.8"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

## Examples

### Tonnes Load States

The following examples demonstrate the load card displaying values in tonnes with different states based on thresholds.

#### Below Target (Neutral)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="0.8"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="0.8"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

#### Above Target (Warning)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="2.5"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="2.5"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

#### Exceeding Alarm Threshold

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="3.1"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="3.1"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

### Percentage Load States

The following examples demonstrate the load card displaying percentage values with different states.

#### At Target (Neutral)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="0.1"
    :type="VariableUnit.Percentage"
    :thresholds="{
      target: 0.1,
      warningHigh: 0.15,
      alarmHigh: 0.28
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="0.1"
    :type="VariableUnit.Percentage"
    :thresholds="{
      target: 0.1,
      warningHigh: 0.15,
      alarmHigh: 0.28
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

#### Above Target (Warning)

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="0.2"
    :type="VariableUnit.Percentage"
    :thresholds="{
      target: 0.1,
      warningHigh: 0.15,
      alarmHigh: 0.28
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="0.2"
    :type="VariableUnit.Percentage"
    :thresholds="{
      target: 0.1,
      warningHigh: 0.15,
      alarmHigh: 0.28
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

#### Exceeding Alarm Threshold

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="0.3"
    :type="VariableUnit.Percentage"
    :thresholds="{
      target: 0.1,
      warningHigh: 0.15,
      alarmHigh: 0.28
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<template>
  <VariableCard
    :value="0.3"
    :type="VariableUnit.Percentage"
    :thresholds="{
      target: 0.1,
      warningHigh: 0.15,
      alarmHigh: 0.28
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>Push</VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

### With Info Tooltip

You can add contextual help using the InfoTooltip component inside the VariableCardTitle.

<div class="my-4 p-8 bg-muted flex justify-center">
  <VariableCard
    :value="2.5"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>
      Push
      <InfoTooltip>
        This value represents the pushing force measured in tonnes. Warning threshold is 2.0t, alarm threshold is 2.8t.
      </InfoTooltip>
    </VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</div>

```vue
<script setup>
import { InfoTooltip } from '@/modules/common/components/info-tooltip'
</script>

<template>
  <VariableCard
    :value="2.5"
    :type="VariableUnit.Tonnes"
    :thresholds="{
      target: 1,
      warningHigh: 2.0,
      alarmHigh: 2.8
    }"
  >
    <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
    <VariableCardValue />
    <VariableCardTitle>
      Push
      <InfoTooltip>
        This value represents the pushing force measured in tonnes. 
        Warning threshold is 2.0t, alarm threshold is 2.8t.
      </InfoTooltip>
    </VariableCardTitle>
    <VariableCardReferenceThresholds />
  </VariableCard>
</template>
```

### All Six Examples in a Grid

<div class="my-4 p-8 bg-muted">
  <div class="grid grid-cols-3 gap-4">
    <VariableCard
      :value="0.8"
      :type="VariableUnit.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="2.5"
      :type="VariableUnit.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="3.1"
      :type="VariableUnit.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="0.1"
      :type="VariableUnit.Percentage"
      :thresholds="{
        target: 0.1,
        warningHigh: 0.15,
        alarmHigh: 0.28
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="0.2"
      :type="VariableUnit.Percentage"
      :thresholds="{
        target: 0.1,
        warningHigh: 0.15,
        alarmHigh: 0.28
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="0.3"
      :type="VariableUnit.Percentage"
      :thresholds="{
        target: 0.1,
        warningHigh: 0.15,
        alarmHigh: 0.28
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
  </div>
</div>

```vue
<template>
  <div class="grid grid-cols-3 gap-4">
    <VariableCard
      :value="0.8"
      :type="VariableUnit.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="2.5"
      :type="VariableUnit.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="3.1"
      :type="VariableUnit.Tonnes"
      :thresholds="{
        target: 1,
        warningHigh: 2.0,
        alarmHigh: 2.8
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="0.1"
      :type="VariableUnit.Percentage"
      :thresholds="{
        target: 0.1,
        warningHigh: 0.15,
        alarmHigh: 0.28
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="0.2"
      :type="VariableUnit.Percentage"
      :thresholds="{
        target: 0.1,
        warningHigh: 0.15,
        alarmHigh: 0.28
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <VariableCard
      :value="0.3"
      :type="VariableUnit.Percentage"
      :thresholds="{
        target: 0.1,
        warningHigh: 0.15,
        alarmHigh: 0.28
      }"
    >
      <VariableCardReferenceTarget>
      <ReferenceBoxLine />
    </VariableCardReferenceTarget>
      <VariableCardValue />
      <VariableCardTitle>Push</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
  </div>
</template>
```

## API Reference

### VariableCard

Container component that provides context for all child components.

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `value` | `number` | Yes | The current variable value to display |
| `type` | `VariableUnit` | Yes | The type of variable - either `VariableUnit.Tonnes` or `VariableUnit.Percentage` |
| `thresholds` | `ReferenceThresholds` | No | Optional threshold values for target, warning, and alarm states |
| `class` | `string` | No | Additional CSS classes to apply to the container |

#### Slots

| Slot | Description |
|------|-------------|
| `default` | Content slot for composing child components (VariableCardReferenceTarget, VariableCardValue, VariableCardTitle, VariableCardReferenceThresholds) |

### VariableCardReferenceTarget

Displays the reference/target box indicator. Consumes context from parent VariableCard.

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `class` | `string` | No | Additional CSS classes to apply |

### VariableCardReferenceThresholds

Displays the alarm threshold indicators (alarmLow and alarmHigh). Consumes context from parent VariableCard.

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `class` | `string` | No | Additional CSS classes to apply |

### VariableCardValue

Displays the numerical value with state-based styling and unit indicator. Consumes context from parent VariableCard.

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `class` | `string` | No | Additional CSS classes to apply |

### VariableCardTitle

Displays the title/label text with consistent styling.

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `class` | `string` | No | Additional CSS classes to apply |

#### Slots

| Slot | Description |
|------|-------------|
| `default` | The title/label text to display |

### ReferenceThresholds Type

```typescript
type ReferenceThresholds = {
  target?: number;          // Target value indicator
  warningLow?: number;      // Low warning threshold
  warningHigh?: number;     // High warning threshold
  alarmLow?: number;        // Low alarm threshold
  alarmHigh?: number;       // High alarm threshold
}
```

### VariableUnit Enum

```typescript
enum VariableUnit {
  Percentage = "percentage",  // Display as percentage
  Tonnes = "tonnes"          // Display as tonnes with 1 decimal place
}
```

## Variable States

The component automatically determines its visual state based on the current value and thresholds:

- **Neutral** - Value is within normal range (between target and warning thresholds)
- **Warning** - Value has exceeded warning threshold but is below alarm threshold
- **Alarm** - Value has exceeded the alarm threshold

The visual state affects the color and appearance of the main value display.

## Usage Guidelines

### When to Use

- Displaying real-time variable measurements with clear threshold indicators
- Showing critical operational values that require monitoring
- Presenting numerical data where exceeding limits has safety implications
- Dashboard displays requiring quick visual status assessment

### When Not to Use

- For text-based content or labels
- When precise threshold monitoring is not required
- For displaying multiple related metrics (consider a table or chart instead)
- When the data doesn't have meaningful thresholds
- For position measurements with sliders (use PositionCard instead)

## Composition Features

- **VariableCardReferenceTarget**: Shows the target value with a visual indicator line when a target threshold is defined
- **VariableCardValue**: Large, prominent display of the current value with state-based coloring and automatic unit label (%, t)
- **VariableCardTitle**: Displays the provided title/label below the main value
- **VariableCardReferenceThresholds**: Shows alarmLow and alarmHigh values at the bottom for reference

## Accessibility

- The component uses semantic HTML structure
- Color coding is supplemented with numerical values for clarity
- Threshold values are always visible for reference
- Title slot provides context for screen readers

## Design Notes

- Values are formatted according to type: percentages show as integers, tonnes show with 1 decimal place
- VariableCardReferenceTarget automatically hides when no target threshold is provided
- All threshold values are optional - the component gracefully handles partial threshold data
- State colors follow the established design system (neutral, warning, alarm)
- The compositional structure allows for flexible layouts and custom arrangements of sub-components
