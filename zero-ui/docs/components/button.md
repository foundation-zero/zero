# Button

Interactive button component with multiple variants and sizes.

## Import

```vue
<script setup lang="ts">
import { Button } from '@/components/ui/shadcn/button'
</script>
```

## Examples

### Default Button

<div style="padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0.5rem; margin: 1rem 0;">
  <p>Example coming soon - interactive demos require a more complex setup</p>
</div>

```vue
<template>
  <Button>Default Button</Button>
</template>
```

### Variants

#### Destructive
```vue
<template>
  <Button variant="destructive">Delete</Button>
</template>
```

#### Outline  
```vue
<template>
  <Button variant="outline">Outline Button</Button>
</template>
```

#### Secondary
```vue
<template>
  <Button variant="secondary">Secondary</Button>
</template>
```

#### Ghost
```vue
<template>
  <Button variant="ghost">Ghost Button</Button>
</template>
```

#### Link
```vue
<template>
  <Button variant="link">Link Button</Button>
</template>
```

### Sizes

#### Small
```vue
<template>
  <Button size="sm">Small Button</Button>
</template>
```

#### Large
```vue
<template>
  <Button size="lg">Large Button</Button>
</template>
```

#### Icon
```vue
<template>
  <Button size="icon">
    <Icon />
  </Button>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `"default" \| "destructive" \| "outline" \| "secondary" \| "ghost" \| "link"` | `"default"` | Visual style variant |
| `size` | `"default" \| "sm" \| "lg" \| "icon"` | `"default"` | Button size |
| `disabled` | `boolean` | `false` | Disable button interaction |
| `as` | `string \| Component` | `"button"` | HTML element or component to render |
| `asChild` | `boolean` | `false` | Render as child element |

## Accessibility

- Uses semantic `<button>` element by default
- Supports keyboard navigation
- Proper ARIA attributes
- Focus management