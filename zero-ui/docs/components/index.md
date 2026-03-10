# Components

Welcome to the Zero UI component library. Below you'll find all available components with live examples and usage instructions.

<script setup>
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
</script>

## Available Components

### UI Components

- [Badge](/components/badge) - Display status and categorization information
- [Button](/components/button) - Interactive button component with multiple variants
- [Input](/components/input) - Text input field for capturing user input
- [Select](/components/select) - Dropdown selection component with enhanced functionality

### Domain Components

- [Loads Card](/components/loads-card) - Visual gauge for displaying load values with target and threshold indicators

## Quick Preview

Here's a quick preview of our components:

### Badge Examples

<div class="my-4 flex gap-2 flex-wrap">
  <Badge>Default</Badge>
  <Badge variant="secondary">Secondary</Badge>
  <Badge variant="destructive">Destructive</Badge>
  <Badge variant="outline">Outline</Badge>
</div>

### Button Examples

<div class="my-4 flex gap-2 flex-wrap">
  <Button>Default</Button>
  <Button variant="destructive">Destructive</Button>
  <Button variant="outline">Outline</Button>
  <Button variant="ghost">Ghost</Button>
</div>

### Input Examples

<div class="my-4 space-y-2 max-w-md">
  <Input placeholder="Basic input example" />
  <Input type="email" placeholder="Email input example" />
  <Input placeholder="Disabled input example" disabled />
</div>

### Select Examples

<div class="my-4 space-y-4 max-w-md">
  <Select>
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