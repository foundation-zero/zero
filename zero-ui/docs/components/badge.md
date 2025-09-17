# Badge

A versatile component for displaying short pieces of information.

<script setup>
import { Badge } from '@/components/ui/shadcn/badge'
</script>

## Overview

The Badge component is used to display labels, statuses, or short pieces of metadata. It supports different visual variants to convey different meanings and contexts.

### Default Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge>Default</Badge>
</div>

```vue
<template>
  <Badge>Default</Badge>
</template>
```

## Examples

### Secondary Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge variant="secondary">Secondary</Badge>
</div>

```vue
<template>
  <Badge variant="secondary">Secondary</Badge>
</template>
```

### Brand Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge variant="brand">Brand</Badge>
</div>

```vue
<template>
  <Badge variant="brand">Brand</Badge>
</template>
```

### Constructive Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge variant="constructive">Constructive</Badge>
</div>

```vue
<template>
  <Badge variant="constructive">Constructive</Badge>
</template>
```

### Warning Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge variant="warning">Warning</Badge>
</div>

```vue
<template>
  <Badge variant="warning">Warning</Badge>
</template>
```

### Destructive Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge variant="destructive">Destructive</Badge>
</div>

```vue
<template>
  <Badge variant="destructive">Destructive</Badge>
</template>
```

### Outline Badge

<div class="my-4 p-4 bg-background-muted">
  <Badge variant="outline">Outline</Badge>
</div>

```vue
<template>
  <Badge variant="outline">Outline</Badge>
</template>
```

### Multiple Badges

<div class="my-4 p-4 bg-background-muted space-x-2">
  <Badge>Default</Badge>
  <Badge variant="secondary">Secondary</Badge>
  <Badge variant="brand">Brand</Badge>
  <Badge variant="outline">Outline</Badge>
</div>

```vue
<template>
  <div class="space-x-2">
    <Badge>Default</Badge>
    <Badge variant="secondary">Secondary</Badge>
    <Badge variant="brand">Brand</Badge>
    <Badge variant="outline">Outline</Badge>
  </div>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'default' \| 'secondary' \| 'brand' \| 'constructive' \| 'warning' \| 'destructive' \| 'outline' | 'default' | The visual style variant |
| class | string | undefined | Additional CSS classes to apply |

## Installation

```vue
<script setup>
import { Badge } from '@/components/ui/shadcn/badge'
</script>

<template>
  <Badge>Badge</Badge>
</template>
```

## Accessibility

- Badges should have appropriate color contrast for readability
- Use semantic meaning for different variants (e.g., destructive for errors)
- Consider screen reader support for decorative badges
- Ensure badges are not the only way to convey important information

## Best Practices

- Use badges sparingly to avoid visual clutter
- Choose appropriate variants based on semantic meaning:
  - **Default**: General purpose labels
  - **Secondary**: Less prominent information
  - **Brand**: Brand-related content or highlights
  - **Constructive**: Success states or positive feedback
  - **Warning**: Caution or attention needed
  - **Destructive**: Errors or dangerous actions
  - **Outline**: Subtle labeling or secondary information
- Ensure proper color contrast for accessibility
- Keep badge text short and descriptive
