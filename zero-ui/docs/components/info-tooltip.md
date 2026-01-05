# Info Tooltip

A simple tooltip component that displays an info icon with additional information on hover or focus.

<script setup>
import { InfoTooltip } from '@/modules/common/components/info-tooltip'
</script>

## Overview

The InfoTooltip component provides a consistent way to display contextual help or additional information. It uses a ghost button with an info icon that triggers a tooltip when hovered or focused.

### Basic Example

<div class="my-4 p-8 bg-muted flex justify-center">
  <InfoTooltip>
    This is helpful information
  </InfoTooltip>
</div>

```vue
<template>
  <InfoTooltip>
    This is helpful information
  </InfoTooltip>
</template>
```

## Examples

### Short Help Text

<div class="my-4 p-8 bg-muted flex justify-center">
  <InfoTooltip>
    Click to edit
  </InfoTooltip>
</div>

```vue
<template>
  <InfoTooltip>
    Click to edit
  </InfoTooltip>
</template>
```

### Detailed Information

<div class="my-4 p-8 bg-muted flex justify-center">
  <InfoTooltip>
    This value represents the current position as a percentage of the total range. Values outside the normal range will trigger warnings or alarms.
  </InfoTooltip>
</div>

```vue
<template>
  <InfoTooltip>
    This value represents the current position as a percentage of the total range. 
    Values outside the normal range will trigger warnings or alarms.
  </InfoTooltip>
</template>
```

### In Context with Text

<div class="my-4 p-8 bg-muted flex justify-center items-center gap-2">
  <span class="text-sm font-medium">Position Value</span>
  <InfoTooltip>
    The position is measured as a percentage (0-1) relative to the full range
  </InfoTooltip>
</div>

```vue
<template>
  <div class="flex items-center gap-2">
    <span class="text-sm font-medium">Position Value</span>
    <InfoTooltip>
      The position is measured as a percentage (0-1) relative to the full range
    </InfoTooltip>
  </div>
</template>
```

## API Reference

### Slots

| Slot | Description |
|------|-------------|
| `default` | The content to display in the tooltip |

## Usage Guidelines

### When to Use

- Providing contextual help for specific fields or values
- Explaining technical terms or acronyms
- Showing additional details without cluttering the interface
- Offering guidance for complex interactions

### When Not to Use

- For critical information that users must see (use visible text instead)
- As a substitute for clear labeling
- For lengthy explanations (consider a help page or documentation instead)
- When the information is already obvious from context

## Accessibility

- The component uses a button element, making it keyboard accessible
- Supports focus and hover interactions
- The info icon provides a visual indicator that additional information is available
- Content should be concise and descriptive

## Design Notes

- Info icon is sized at 5 units (size-5) for optimal visibility
- Tooltip appears on hover or focus with appropriate positioning
- Consistent with shadcn/ui tooltip patterns
