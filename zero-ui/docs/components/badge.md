# Badge

Small status indicators and labels for categorizing content and conveying information at a glance.

## Import

```vue
<script setup lang="ts">
import { Badge } from '@/components/ui/shadcn/badge'
</script>
```

## Examples

### Default Badge

```vue
<template>
  <Badge>Default</Badge>
</template>
```

### Variants

#### Secondary
```vue
<template>
  <Badge variant="secondary">Secondary</Badge>
</template>
```

#### Brand
```vue
<template>
  <Badge variant="brand">Brand</Badge>
</template>
```

#### Constructive
```vue
<template>
  <Badge variant="constructive">Success</Badge>
</template>
```

#### Warning
```vue
<template>
  <Badge variant="warning">Warning</Badge>
</template>
```

#### Destructive
```vue
<template>
  <Badge variant="destructive">Error</Badge>
</template>
```

#### Outline
```vue
<template>
  <Badge variant="outline">Outline</Badge>
</template>
```

### With Icons

```vue
<script setup lang="ts">
import { Badge } from '@/components/ui/shadcn/badge'
import { CheckIcon, AlertTriangleIcon } from 'lucide-vue-next'
</script>

<template>
  <div class="flex gap-2">
    <Badge variant="constructive">
      <CheckIcon />
      Verified
    </Badge>
    
    <Badge variant="warning">
      <AlertTriangleIcon />
      Warning
    </Badge>
  </div>
</template>
```

### As Links

```vue
<template>
  <div class="flex gap-2">
    <Badge as="a" href="#" variant="brand">
      Clickable Badge
    </Badge>
    
    <Badge as="button" variant="outline" @click="handleClick">
      Button Badge
    </Badge>
  </div>
</template>
```

### Use Cases

#### Status Indicators
```vue
<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <span>Order Status:</span>
      <Badge variant="constructive">Completed</Badge>
    </div>
    
    <div class="flex items-center gap-2">
      <span>Payment:</span>
      <Badge variant="warning">Pending</Badge>
    </div>
    
    <div class="flex items-center gap-2">
      <span>Subscription:</span>
      <Badge variant="destructive">Expired</Badge>
    </div>
  </div>
</template>
```

#### Tags and Categories
```vue
<template>
  <div class="flex flex-wrap gap-1">
    <Badge variant="secondary">React</Badge>
    <Badge variant="secondary">Vue</Badge>
    <Badge variant="secondary">TypeScript</Badge>
    <Badge variant="secondary">Tailwind</Badge>
  </div>
</template>
```

#### Notifications
```vue
<template>
  <div class="flex items-center gap-2">
    <span>Messages</span>
    <Badge variant="destructive">3</Badge>
  </div>
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `"default" \| "secondary" \| "brand" \| "constructive" \| "warning" \| "destructive" \| "outline"` | `"default"` | Visual style variant |
| `as` | `string \| Component` | `"span"` | HTML element or component to render |
| `asChild` | `boolean` | `false` | Render as child element |
| `class` | `string` | `undefined` | Additional CSS classes |

## Variants

| Variant | Description | Use Case |
|---------|-------------|----------|
| `default` | High contrast dark badge | Primary labels, important information |
| `secondary` | Subtle neutral badge | Tags, categories, secondary information |
| `brand` | Brand colored badge | Promotional content, brand highlights |
| `constructive` | Success/positive badge | Success states, completed actions |
| `warning` | Warning/caution badge | Warnings, pending states |
| `destructive` | Error/danger badge | Errors, failures, urgent attention |
| `outline` | Outlined badge | Subtle emphasis, low priority information |

## Accessibility

- Uses semantic HTML elements
- Supports keyboard navigation when used as interactive elements
- Proper contrast ratios for all variants
- Screen reader compatible
- Focus management with visible focus indicators

## Design Guidelines

### When to Use
- **Status indicators** - Show the state of an item or process
- **Categories and tags** - Group and organize content
- **Counts and notifications** - Display numeric values or alerts
- **Labels** - Add descriptive information to elements

### When Not to Use
- **Large amounts of text** - Use cards or other components instead
- **Primary actions** - Use buttons for main interactions
- **Complex information** - Consider tooltips or other components

### Best Practices
- Keep text concise and clear
- Use consistent variants for similar types of information
- Don't overuse badges as they can create visual clutter
- Ensure proper color contrast for accessibility