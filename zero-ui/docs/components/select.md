# Select

A dropdown selection component built on top of Reka UI with enhanced accessibility and styling.

<script setup>
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectItemText,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectTriggerLabel,
  SelectValue
} from '@/components/ui/shadcn/select'
</script>

## Overview

The Select component provides a clean, accessible way to choose from a list of options. It supports grouping, separators, custom styling, and full keyboard navigation.

## Examples

### Basic Select

<div class="my-4">
  <Select>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select a fruit" />
      <SelectTriggerLabel>Fruit</SelectTriggerLabel>
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="apple">Apple</SelectItem>
      <SelectItem value="banana">Banana</SelectItem>
      <SelectItem value="orange">Orange</SelectItem>
      <SelectItem value="grape">Grape</SelectItem>
    </SelectContent>
  </Select>
</div>

```vue
<template>
  <Select>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select a fruit" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="apple">Apple</SelectItem>
      <SelectItem value="banana">Banana</SelectItem>
      <SelectItem value="orange">Orange</SelectItem>
      <SelectItem value="grape">Grape</SelectItem>
    </SelectContent>
  </Select>
</template>
```

### Grouped Options

<div class="my-4">
  <Select>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select a framework" />
    </SelectTrigger>
    <SelectContent>
      <SelectGroup>
        <SelectLabel>Frontend</SelectLabel>
        <SelectItem value="vue">Vue.js</SelectItem>
        <SelectItem value="react">React</SelectItem>
        <SelectItem value="angular">Angular</SelectItem>
      </SelectGroup>
      <SelectSeparator />
      <SelectGroup>
        <SelectLabel>Backend</SelectLabel>
        <SelectItem value="node">Node.js</SelectItem>
        <SelectItem value="python">Python</SelectItem>
        <SelectItem value="go">Go</SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
</div>

```vue
<template>
  <Select>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select a framework" />
    </SelectTrigger>
    <SelectContent>
      <SelectGroup>
        <SelectLabel>Frontend</SelectLabel>
        <SelectItem value="vue">Vue.js</SelectItem>
        <SelectItem value="react">React</SelectItem>
        <SelectItem value="angular">Angular</SelectItem>
      </SelectGroup>
      <SelectSeparator />
      <SelectGroup>
        <SelectLabel>Backend</SelectLabel>
        <SelectItem value="node">Node.js</SelectItem>
        <SelectItem value="python">Python</SelectItem>
        <SelectItem value="go">Go</SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
</div>
```

### With Disabled Options

<div class="my-4">
  <Select>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select a status" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="active">Active</SelectItem>
      <SelectItem value="inactive">Inactive</SelectItem>
      <SelectItem value="pending" disabled>Pending (Coming Soon)</SelectItem>
      <SelectItem value="archived">Archived</SelectItem>
    </SelectContent>
  </Select>
</div>

```vue
<template>
  <Select>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select a status" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="active">Active</SelectItem>
      <SelectItem value="inactive">Inactive</SelectItem>
      <SelectItem value="pending" disabled>Pending (Coming Soon)</SelectItem>
      <SelectItem value="archived">Archived</SelectItem>
    </SelectContent>
  </Select>
</template>
```

### Different Sizes

<div class="my-4 space-y-4">
  <Select>
    <SelectTrigger class="w-[280px]" size="sm">
      <SelectValue placeholder="Small select" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="small">Small Option</SelectItem>
      <SelectItem value="medium">Medium Option</SelectItem>
    </SelectContent>
  </Select>
  
  <Select>
    <SelectTrigger class="w-[280px]" size="default">
      <SelectValue placeholder="Default select" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="small">Small Option</SelectItem>
      <SelectItem value="medium">Medium Option</SelectItem>
    </SelectContent>
  </Select>
</div>

```vue
<template>
  <div class="space-y-4">
    <!-- Small size -->
    <Select>
      <SelectTrigger class="w-[280px]" size="sm">
        <SelectValue placeholder="Small select" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="small">Small Option</SelectItem>
        <SelectItem value="medium">Medium Option</SelectItem>
      </SelectContent>
    </Select>
    
    <!-- Default size -->
    <Select>
      <SelectTrigger class="w-[280px]" size="default">
        <SelectValue placeholder="Default select" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="small">Small Option</SelectItem>
        <SelectItem value="medium">Medium Option</SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
```

### Multiple Selection

<div class="my-4">
  <Select multiple>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select multiple options" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="react">React</SelectItem>
      <SelectItem value="vue">Vue</SelectItem>
      <SelectItem value="angular">Angular</SelectItem>
      <SelectItem value="svelte">Svelte</SelectItem>
      <SelectItem value="solid">SolidJS</SelectItem>
    </SelectContent>
  </Select>
</div>

```vue
<template>
  <Select multiple>
    <SelectTrigger class="w-[280px]">
      <SelectValue placeholder="Select multiple options" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="react">React</SelectItem>
      <SelectItem value="vue">Vue</SelectItem>
      <SelectItem value="angular">Angular</SelectItem>
      <SelectItem value="svelte">Svelte</SelectItem>
      <SelectItem value="solid">SolidJS</SelectItem>
    </SelectContent>
  </Select>
</template>
```

### Multiple Select with counter

<div class="my-4">
  <Select multiple>
    <MultiSelectTrigger>
      <MultiSelectValue>Add</MultiSelectValue>
    </MultiSelectTrigger>
    <SelectContent>
      <SelectItem value="react">React</SelectItem>
      <SelectItem value="vue">Vue</SelectItem>
      <SelectItem value="angular">Angular</SelectItem>
      <SelectItem value="svelte">Svelte</SelectItem>
      <SelectItem value="solid">SolidJS</SelectItem>
    </SelectContent>
  </Select>
</div>

```vue
<template>
  <Select multiple>
    <MultiSelectTrigger>
      <MultiSelectValue>Add</MultiSelectValue>
    </MultiSelectTrigger>
    <SelectContent>
      <SelectItem value="react">React</SelectItem>
      <SelectItem value="vue">Vue</SelectItem>
      <SelectItem value="angular">Angular</SelectItem>
      <SelectItem value="svelte">Svelte</SelectItem>
      <SelectItem value="solid">SolidJS</SelectItem>
    </SelectContent>
  </Select>
</template>
```

## API Reference

### Select

The root container for the select component.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string \| string[]` | `undefined` | The controlled value of the select. When multiple is true, this becomes an array |
| `defaultValue` | `string \| string[]` | `undefined` | The default value when uncontrolled. When multiple is true, this can be an array |
| `multiple` | `boolean` | `false` | Whether multiple options can be selected or not |
| `open` | `boolean` | `undefined` | Controls the open state |
| `defaultOpen` | `boolean` | `false` | The default open state when uncontrolled |
| `disabled` | `boolean` | `false` | When true, prevents user interaction |
| `required` | `boolean` | `false` | When true, indicates that the user must select a value |

### SelectTrigger

The button that toggles the select dropdown.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'default'` | `'default'` | The size of the trigger button |
| `class` | `string` | `undefined` | Additional CSS classes |
| `disabled` | `boolean` | `false` | When true, prevents user interaction |

### SelectContent

The component that contains the select items.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `position` | `'item-aligned' \| 'popper'` | `'popper'` | The positioning strategy |
| `side` | `'top' \| 'right' \| 'bottom' \| 'left'` | `'bottom'` | The preferred side of the anchor to render against |
| `align` | `'start' \| 'center' \| 'end'` | `'start'` | The preferred alignment against the anchor |
| `class` | `string` | `undefined` | Additional CSS classes |

### SelectItem

An item in the select list.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `string` | `undefined` | The value associated with the item |
| `disabled` | `boolean` | `false` | When true, prevents user interaction |
| `textValue` | `string` | `undefined` | Optional text used for typeahead purposes |
| `class` | `string` | `undefined` | Additional CSS classes |

### SelectValue

Displays the selected value or placeholder.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `placeholder` | `string` | `undefined` | The content that will be rendered when no value is selected |
| `class` | `string` | `undefined` | Additional CSS classes |

### SelectLabel

Used to render a label in a group.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `class` | `string` | `undefined` | Additional CSS classes |

### SelectSeparator

Used to visually separate items in the select.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `class` | `string` | `undefined` | Additional CSS classes |

## Installation

```vue
<script setup>
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectItemText,
  SelectLabel,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectSeparator,
  SelectTrigger,
  SelectValue
} from '@/components/ui/shadcn/select'
</script>

<template>
  <div>
    <Select v-model="selectedValue" @update:model-value="handleValueChange">
      <SelectTrigger>
        <SelectValue placeholder="Select an option" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="option1">Option 1</SelectItem>
        <SelectItem value="option2">Option 2</SelectItem>
        <SelectItem value="option3">Option 3</SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
```

## Accessibility

The Select component follows WAI-ARIA guidelines and includes:

- **Keyboard Navigation**: Full keyboard support with arrow keys, Enter/Space, and Escape
- **Screen Reader Support**: Proper ARIA labels and announcements
- **Focus Management**: Predictable focus behavior and visible focus indicators
- **High Contrast**: Support for high contrast mode and color preferences

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` or `Enter` | Open/close select or select focused option |
| `ArrowUp/ArrowDown` | Navigate options |
| `Home/End` | Jump to first/last option |
| `Enter` or `Space` | Select focused option |
| `Escape` | Close select |
| `A-Z, 0-9` | Type-ahead search |
| `Tab` | Move to next focusable element |

## Best Practices

- Use clear, descriptive option labels that make sense out of context
- Include meaningful placeholder text that describes the expected selection
- Group related options using `SelectGroup` and `SelectLabel` for better organization
- Use `disabled` state for temporarily unavailable options rather than hiding them
- Ensure sufficient color contrast for all interactive states
- Test thoroughly with keyboard navigation and screen readers
- Consider the dropdown position relative to viewport edges
- Provide loading states when options are fetched asynchronously

## Form Integration

### Single Selection Form

```vue
<script setup>
import { ref } from 'vue'
import { useForm } from 'vee-validate'
import * as yup from 'yup'

const schema = yup.object({
  country: yup.string().required('Please select a country'),
})

const { handleSubmit, errors, defineField } = useForm({
  validationSchema: schema,
})

const [country, countryAttrs] = defineField('country')

const onSubmit = handleSubmit((values) => {
  console.log('Form submitted:', values)
})
</script>

<template>
  <form @submit="onSubmit">
    <div class="space-y-2">
      <label class="text-sm font-medium">Country</label>
      <Select v-model="country" v-bind="countryAttrs" :class="{ 'border-destructive': errors.country }">
        <SelectTrigger>
          <SelectValue placeholder="Select your country" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="us">United States</SelectItem>
          <SelectItem value="ca">Canada</SelectItem>
          <SelectItem value="uk">United Kingdom</SelectItem>
        </SelectContent>
      </Select>
      <p v-if="errors.country" class="text-sm text-destructive">{{ errors.country }}</p>
    </div>
    <button type="submit" class="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded">
      Submit
    </button>
  </form>
</template>
```

### Multiple Selection Form

```vue
<script setup>
import { ref } from 'vue'
import { useForm } from 'vee-validate'
import * as yup from 'yup'

const schema = yup.object({
  skills: yup.array().of(yup.string()).min(1, 'Please select at least one skill'),
})

const { handleSubmit, errors, defineField } = useForm({
  validationSchema: schema,
})

const [skills, skillsAttrs] = defineField('skills')

const onSubmit = handleSubmit((values) => {
  console.log('Form submitted:', values)
})
</script>

<template>
  <form @submit="onSubmit">
    <div class="space-y-2">
      <label class="text-sm font-medium">Skills</label>
      <Select 
        v-model="skills" 
        v-bind="skillsAttrs" 
        multiple
        :class="{ 'border-destructive': errors.skills }"
      >
        <SelectTrigger>
          <SelectValue placeholder="Select your skills" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="javascript">JavaScript</SelectItem>
          <SelectItem value="typescript">TypeScript</SelectItem>
          <SelectItem value="vue">Vue.js</SelectItem>
          <SelectItem value="react">React</SelectItem>
          <SelectItem value="node">Node.js</SelectItem>
          <SelectItem value="python">Python</SelectItem>
        </SelectContent>
      </Select>
      <p v-if="errors.skills" class="text-sm text-destructive">{{ errors.skills }}</p>
    </div>
    <button type="submit" class="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded">
      Submit
    </button>
  </form>
</template>
```

## Usage with v-model

### Single Selection

```vue
<script setup>
import { ref } from 'vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/shadcn/select'

const selectedValue = ref('')

function handleValueChange(value: string) {
  console.log('Selected:', value)
}
</script>

<template>
  <div>
    <Select v-model="selectedValue" @update:model-value="handleValueChange">
      <SelectTrigger>
        <SelectValue placeholder="Select an option" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="option1">Option 1</SelectItem>
        <SelectItem value="option2">Option 2</SelectItem>
        <SelectItem value="option3">Option 3</SelectItem>
      </SelectContent>
    </Select>
    
    <p class="mt-2 text-sm">Selected: {{ selectedValue || 'None' }}</p>
  </div>
</template>
```

### Multiple Selection

```vue
<script setup>
import { ref } from 'vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/shadcn/select'

const selectedValues = ref([])

function handleValueChange(values: string[]) {
  console.log('Selected values:', values)
}
</script>

<template>
  <div>
    <Select v-model="selectedValues" multiple @update:model-value="handleValueChange">
      <SelectTrigger>
        <SelectValue placeholder="Select multiple options" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="react">React</SelectItem>
        <SelectItem value="vue">Vue</SelectItem>
        <SelectItem value="angular">Angular</SelectItem>
        <SelectItem value="svelte">Svelte</SelectItem>
      </SelectContent>
    </Select>
    
    <div class="mt-2 text-sm">
      <p>Selected: {{ selectedValues.length > 0 ? selectedValues.join(', ') : 'None' }}</p>
      <p>Count: {{ selectedValues.length }}</p>
    </div>
  </div>
</template>
```
