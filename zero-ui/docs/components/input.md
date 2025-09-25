# Input

A basic input field component for capturing user input.

<script setup>
import { Input } from '@/components/ui/shadcn/input'
</script>

## Overview

The Input component is a styled HTML input element that supports various types and states. It's built with accessibility and form validation in mind.

### Basic Input

<div class="my-4  p-4 bg-muted">
  <Input placeholder="Enter your name..." />
</div>

```vue
<template>
  <Input placeholder="Enter your name..." />
</template>
```

## Examples

### Text Input

<div class="my-4 p-4 bg-muted">
  <Input type="text" placeholder="Enter text..." />
</div>

```vue
<template>
  <Input type="text" placeholder="Enter text..." />
</template>
```

### Email Input

<div class="my-4 p-4 bg-muted">
  <Input type="email" placeholder="Enter your email..." />
</div>

```vue
<template>
  <Input type="email" placeholder="Enter your email..." />
</template>
```

### Password Input

<div class="my-4 p-4 bg-muted">
  <Input type="password" placeholder="Enter password..." />
</div>

```vue
<template>
  <Input type="password" placeholder="Enter password..." />
</template>
```

### Disabled Input

<div class="my-4 p-4 bg-muted">
  <Input placeholder="Disabled input" disabled />
</div>

```vue
<template>
  <Input placeholder="Disabled input" disabled />
</template>
```

### Input with validation

<div class="my-4 p-4 bg-muted">
  <Input placeholder="Invalid input" invalid />
</div>

```vue
<template>
  <Input placeholder="Invalid input" invalid />
</template>
```

## Usage with v-model

```vue
<script setup>
import { ref } from 'vue'
import { Input } from '@/components/ui/shadcn/input'

const inputValue = ref('')
</script>

<template>
  <Input v-model="inputValue" placeholder="Type something..." />
  <p>Current value: {{ inputValue }}</p>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string \| number` | `undefined` | The input value (for v-model) |
| `defaultValue` | `string \| number` | `undefined` | Default value for the input |
| `class` | `string` | `undefined` | Additional CSS classes |
| `type` | `string` | `"text"` | HTML input type |
| `placeholder` | `string` | `undefined` | Placeholder text |
| `disabled` | `boolean` | `false` | Whether the input is disabled |

## Events

| Event | Type | Description |
|-------|------|-------------|
| `update:modelValue` | `(value: string \| number) => void` | Emitted when the input value changes |

## Accessibility

- Supports all standard HTML input attributes
- Proper focus management with visible focus ring
- Screen reader compatible
- Keyboard navigation support
- Form validation states with visual feedback

## Styling

The Input component automatically adapts to your theme colors and includes:

- **Focus states**: Ring and border color changes on focus
- **Error states**: Red border and ring for validation errors
- **Disabled states**: Reduced opacity and pointer events disabled
- **File input styling**: Custom styling for file selection
- **Dark mode support**: Automatic adaptation to dark themes