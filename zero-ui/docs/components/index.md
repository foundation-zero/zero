# Components

Welcome to the Zero UI component library. Below you'll find all available components with live examples and usage instructions.

## Available Components

### Form Components
- [Button](/components/button) - Interactive buttons with multiple variants
- [Checkbox](/components/checkbox) - Form input controls

### Layout Components  
- [Card](/components/card) - Content containers

## Usage Pattern

All components follow a consistent API pattern:

```vue
<script setup lang="ts">
import { ComponentName } from '@/components/ui/shadcn/component-name'
</script>

<template>
  <ComponentName variant="default" size="md">
    Content
  </ComponentName>
</template>
```

## Styling

Components are built with:
- **Tailwind CSS** for utility-first styling
- **Class Variance Authority (CVA)** for variant management
- **Tailwind Merge** for class optimization
- **shadcn/ui** design principles