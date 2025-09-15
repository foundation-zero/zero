# Components

Welcome to the Zero UI component library. Below you'll find all available components with live examples and usage instructions.

<script setup>
import { Badge } from '@/components/ui/shadcn/badge'
import { Input } from '@/components/ui/shadcn/input'
</script>

## Available Components

### UI Components

- [Badge](/components/badge) - Display status and categorization information
- [Input](/components/input) - Text input field for capturing user input

## Quick Preview

Here's a quick preview of our components:

### Badge Examples

<div class="my-4 flex gap-2 flex-wrap">
  <Badge>Default</Badge>
  <Badge variant="secondary">Secondary</Badge>
  <Badge variant="destructive">Destructive</Badge>
  <Badge variant="outline">Outline</Badge>
</div>

### Input Examples

<div class="my-4 space-y-2 max-w-md">
  <Input placeholder="Basic input example" />
  <Input type="email" placeholder="Email input example" />
  <Input placeholder="Disabled input example" disabled />
</div>

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