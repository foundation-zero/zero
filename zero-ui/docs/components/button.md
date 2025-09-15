# Button

A versatile button component with multiple variants and sizes for different use cases.

<script setup>
import { Button } from '@/components/ui/shadcn/button'
</script>

## Overview

The Button component is a fundamental UI element for triggering actions and navigation. It supports multiple visual variants, sizes, and states to provide clear user interaction patterns.

### Default Button

<div class="my-4 p-4 bg-background-muted">
  <Button>Default Button</Button>
</div>

```vue
<template>
  <Button>Default Button</Button>
</template>
```

## Examples

### Destructive Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="destructive">Delete Item</Button>
</div>

```vue
<template>
  <Button variant="destructive">Delete Item</Button>
</template>
```

### Constructive Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="constructive">Save Changes</Button>
</div>

```vue
<template>
  <Button variant="constructive">Save Changes</Button>
</template>
```

### Warning Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="warning">Warning Action</Button>
</div>

```vue
<template>
  <Button variant="warning">Warning Action</Button>
</template>
```

### Brand Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="brand">Brand Action</Button>
</div>

```vue
<template>
  <Button variant="brand">Brand Action</Button>
</template>
```

### Outline Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="outline">Outline Button</Button>
</div>

```vue
<template>
  <Button variant="outline">Outline Button</Button>
</template>
```

### Secondary Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="secondary">Secondary Action</Button>
</div>

```vue
<template>
  <Button variant="secondary">Secondary Action</Button>
</template>
```

### Ghost Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="ghost">Ghost Button</Button>
</div>

```vue
<template>
  <Button variant="ghost">Ghost Button</Button>
</template>
```

### Link Button

<div class="my-4 p-4 bg-background-muted">
  <Button variant="link">Link Button</Button>
</div>

```vue
<template>
  <Button variant="link">Link Button</Button>
</template>
```

## Sizes

### Small Button

<div class="my-4 p-4 bg-background-muted">
  <Button size="sm">Small Button</Button>
</div>

```vue
<template>
  <Button size="sm">Small Button</Button>
</template>
```

### Default Size

<div class="my-4 p-4 bg-background-muted">
  <Button>Default Size</Button>
</div>

```vue
<template>
  <Button>Default Size</Button>
</template>
```

### Large Button

<div class="my-4 p-4 bg-background-muted">
  <Button size="lg">Large Button</Button>
</div>

```vue
<template>
  <Button size="lg">Large Button</Button>
</template>
```

### Icon Button

<div class="my-4 p-4 bg-background-muted">
  <Button size="icon" variant="outline">
    <svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
    </svg>
  </Button>
</div>

```vue
<template>
  <Button size="icon" variant="outline">
    <PlusIcon class="size-4" />
  </Button>
</template>
```

## States

### Disabled Button

<div class="my-4 p-4 bg-background-muted space-x-2 flex flex-wrap gap-2">
  <Button disabled>Disabled Default</Button>
  <Button variant="destructive" disabled>Disabled Destructive</Button>
  <Button variant="constructive" disabled>Disabled Constructive</Button>
  <Button variant="warning" disabled>Disabled Warning</Button>
  <Button variant="outline" disabled>Disabled Outline</Button>
</div>

```vue
<template>
  <Button disabled>Disabled Button</Button>
</template>
```

### Button Combinations

<div class="my-4 p-4 bg-background-muted space-x-2">
  <Button>Primary Action</Button>
  <Button variant="outline">Secondary</Button>
  <Button variant="ghost">Cancel</Button>
</div>

```vue
<template>
  <div class="space-x-2">
    <Button>Primary Action</Button>
    <Button variant="outline">Secondary</Button>
    <Button variant="ghost">Cancel</Button>
  </div>
</template>
```

### All Variants

<div class="my-4 p-4 bg-background-muted space-x-2 flex flex-wrap gap-2">
  <Button variant="default">Default</Button>
  <Button variant="destructive">Destructive</Button>
  <Button variant="constructive">Constructive</Button>
  <Button variant="warning">Warning</Button>
  <Button variant="brand">Brand</Button>
  <Button variant="outline">Outline</Button>
  <Button variant="secondary">Secondary</Button>
  <Button variant="ghost">Ghost</Button>
  <Button variant="link">Link</Button>
</div>

```vue
<template>
  <div class="space-x-2 flex flex-wrap gap-2">
    <Button variant="default">Default</Button>
    <Button variant="destructive">Destructive</Button>
    <Button variant="constructive">Constructive</Button>
    <Button variant="warning">Warning</Button>
    <Button variant="brand">Brand</Button>
    <Button variant="outline">Outline</Button>
    <Button variant="secondary">Secondary</Button>
    <Button variant="ghost">Ghost</Button>
    <Button variant="link">Link</Button>
  </div>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'default' \| 'destructive' \| 'constructive' \| 'warning' \| 'brand' \| 'outline' \| 'secondary' \| 'ghost' \| 'link' | 'default' | The visual style variant |
| size | 'default' \| 'sm' \| 'lg' \| 'icon' | 'default' | The button size |
| as | string \| Component | 'button' | The element or component to render as |
| asChild | boolean | false | Whether to render as a child element |
| class | string | undefined | Additional CSS classes to apply |
| disabled | boolean | false | Whether the button is disabled |

## Installation

```vue
<script setup>
import { Button } from '@/components/ui/shadcn/button'
</script>

<template>
  <Button>Click me</Button>
</template>
```

## Accessibility

- Buttons should have clear, descriptive text or accessible labels
- Use appropriate button types (button, submit, reset) for form contexts
- Disabled buttons should be properly indicated to screen readers
- Icon-only buttons should include aria-label attributes
- Ensure sufficient color contrast for all variants
- Support keyboard navigation and focus states

## Best Practices

- **Choose appropriate variants based on action hierarchy:**
  - **Default**: Primary actions and main calls-to-action
  - **Destructive**: Delete, remove, or dangerous actions
  - **Outline**: Secondary actions or alternative options
  - **Secondary**: Less prominent actions
  - **Ghost**: Subtle actions, often used in toolbars
  - **Link**: Navigation or actions that behave like links

- **Use consistent sizing:**
  - **Small**: Compact interfaces, tables, or secondary actions
  - **Default**: Standard interface elements
  - **Large**: Prominent calls-to-action or hero sections
  - **Icon**: Icon-only actions, toolbars, or compact interfaces

- **Action hierarchy**: Use no more than one primary button per section
- **Loading states**: Consider adding loading indicators for async actions
- **Responsive design**: Test button sizes across different screen sizes
- **Clear labeling**: Use action-oriented, specific button text