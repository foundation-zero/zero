# Checkbox

Form input component for boolean selections with proper accessibility support.

## Import

```vue
<script setup lang="ts">
import { Checkbox } from '@/components/ui/shadcn/checkbox'
</script>
```

## Examples

### Basic Checkbox

```vue
<template>
  <div class="flex items-center space-x-2">
    <Checkbox id="basic" />
    <label for="basic">Accept terms and conditions</label>
  </div>
</template>
```

### Checked by Default

```vue
<template>
  <div class="flex items-center space-x-2">
    <Checkbox id="checked" :default-checked="true" />
    <label for="checked">Subscribe to newsletter</label>
  </div>
</template>
```

### Disabled State

```vue
<template>
  <div class="flex items-center space-x-2">
    <Checkbox id="disabled" disabled />
    <label for="disabled" class="opacity-50">
      Disabled checkbox
    </label>
  </div>
</template>
```

### Controlled Checkbox

```vue
<script setup lang="ts">
import { ref } from 'vue'

const checked = ref(false)
</script>

<template>
  <div class="flex items-center space-x-2">
    <Checkbox 
      id="controlled" 
      v-model:checked="checked"
    />
    <label for="controlled">
      Controlled: {{ checked ? 'Checked' : 'Unchecked' }}
    </label>
  </div>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `string` | - | Unique identifier for the checkbox |
| `checked` | `boolean` | `undefined` | Controlled checked state |
| `defaultChecked` | `boolean` | `false` | Default checked state (uncontrolled) |
| `disabled` | `boolean` | `false` | Disable the checkbox |
| `required` | `boolean` | `false` | Mark as required field |
| `name` | `string` | - | Form field name |

## Events

| Event | Type | Description |
|-------|------|-------------|
| `update:checked` | `(checked: boolean) => void` | Emitted when checked state changes |

## Accessibility

- Uses proper ARIA attributes
- Supports keyboard navigation (Space to toggle)
- Screen reader compatible
- Focus management with visible focus indicators
- Proper labeling support with `id` and `for` attributes