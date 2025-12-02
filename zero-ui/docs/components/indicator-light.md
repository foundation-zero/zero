# Indicator Light

A visual indicator component that displays status using illuminated circular lights with realistic glass effects.

<script setup>
import { IndicatorLight } from '@/modules/loads/components/indicator-light'
</script>

## Overview

The IndicatorLight component provides a realistic LED indicator with glass-like appearance and glow effects. It's ideal for displaying system status, active states, or alert conditions in a visually distinctive way.

### Default Light

<div class="my-4 p-8 bg-background flex justify-center">
  <IndicatorLight />
</div>
 
```vue
<template>
  <IndicatorLight />
</template>
```

## Examples

### Default Variant

The default variant displays a subtle, inactive indicator with a dark appearance.

<div class="my-4 p-8 bg-background flex justify-center">
  <IndicatorLight variant="default" />
</div>

```vue
<template>
  <IndicatorLight variant="default" />
</template>
```

### Constructive Variant

The constructive variant uses a green glow to indicate positive status, success, or active operation.

<div class="my-4 p-8 bg-background flex justify-center">
  <IndicatorLight variant="constructive" />
</div>

```vue
<template>
  <IndicatorLight variant="constructive" />
</template>
```

### Destructive Variant

The destructive variant uses a red glow to indicate errors, alerts, or critical conditions.

<div class="my-4 p-8 bg-background flex justify-center">
  <IndicatorLight variant="destructive" />
</div>

```vue
<template>
  <IndicatorLight variant="destructive" />
</template>
```

### Multiple Indicators

Multiple indicators can be arranged together to create status panels or control displays.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-4 justify-center">
    <IndicatorLight variant="default" />
    <IndicatorLight variant="constructive" />
    <IndicatorLight variant="destructive" />
  </div>
</div>

```vue
<template>
  <div class="flex gap-4">
    <IndicatorLight variant="default" />
    <IndicatorLight variant="constructive" />
    <IndicatorLight variant="destructive" />
  </div>
</template>
```

### With Labels

Indicators can be combined with labels for clarity.

<div class="my-4 p-8 bg-background">
  <div class="flex gap-6 justify-center">
    <div class="flex flex-col items-center gap-2">
      <IndicatorLight variant="default" />
      <span class="text-xs text-muted-foreground">Standby</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <IndicatorLight variant="constructive" />
      <span class="text-xs text-muted-foreground">Active</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <IndicatorLight variant="destructive" />
      <span class="text-xs text-muted-foreground">Alert</span>
    </div>
  </div>
</div>

```vue
<template>
  <div class="flex gap-6">
    <div class="flex flex-col items-center gap-2">
      <IndicatorLight variant="default" />
      <span class="text-xs text-muted-foreground">Standby</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <IndicatorLight variant="constructive" />
      <span class="text-xs text-muted-foreground">Active</span>
    </div>
    <div class="flex flex-col items-center gap-2">
      <IndicatorLight variant="destructive" />
      <span class="text-xs text-muted-foreground">Alert</span>
    </div>
  </div>
</template>
```

## API Reference

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'default' \| 'constructive' \| 'destructive'` | `'default'` | Visual variant of the indicator |
| `class` | `string` | - | Additional CSS classes for the glass element |

## Variants

### default
An inactive or neutral state indicator with a subtle dark appearance and inner shadow.

### constructive
A positive state indicator with a green glow, typically used to show:
- Active/running status
- Success states
- Operational conditions
- System ready states

### destructive
A warning or error state indicator with a red glow, typically used to show:
- Error conditions
- Alert states
- Critical warnings
- System faults

## Usage Guidelines

### When to Use

- **Status Indicators**: Display system or component operational status
- **Alert Panels**: Show critical conditions or warnings
- **Control Panels**: Indicate which controls or systems are active
- **Monitoring Displays**: Provide at-a-glance status information

### When Not to Use

- **Text Information**: Use badges or labels for displaying text
- **Interactive Controls**: Use buttons or switches for user interaction
- **Progress Indication**: Use progress bars or spinners for loading states
- **Large Amounts of Data**: Use tables or charts for detailed information

## Accessibility

- The indicator is purely visual and should be accompanied by text labels or `aria-label` attributes
- Consider providing text alternatives for screen readers
- Ensure sufficient color contrast in the surrounding context
- Don't rely solely on color to convey meaning

## Design Notes

The component features a realistic glass effect achieved through:
- Radial gradient highlight for glass reflection
- Variant-specific glow using box-shadow
- Color-coded illumination states
- Circular housing with muted background
