# Popover

A floating panel that displays rich content in a portal, triggered by user interaction.

<script setup>
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/shadcn/popover'
import { Button } from '@/components/ui/shadcn/button'
</script>

## Overview

The Popover component displays floating content that appears on top of other page content. It's useful for displaying additional information, menus, or interactive elements without navigating away from the current context.

### Sail select

<div class="my-4 p-8 bg-muted flex justify-center">
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline">Sail select</Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto">
      <div class="space-y-2">
        <h4 class="font-semibold">Main</h4>
        <div class="flex flex-nowrap gap-2 mt-3 items-center">
          <header class="w-12">Sail</header>
          <Button variant="outline" size="sm">Option 1</Button>
          <Button variant="outline" size="sm">Option 2</Button>
          <Button variant="outline" size="sm">Option 3</Button>
        </div>
        <div class="flex flex-nowrap gap-2 mt-3 items-center">
          <header class="w-12">Blade</header>
          <Button variant="outline" size="sm">Yes</Button>
          <Button variant="outline" size="sm">No</Button>
        </div>
        <div class="flex flex-nowrap gap-2 mt-3 items-center">
          <header class="w-12">Reefs</header>
          <Button variant="outline" size="sm">Reef 1</Button>
          <Button variant="outline" size="sm">Reef 2</Button>
          <Button variant="outline" size="sm">Reef 3</Button>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</div>

```vue
<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline">Sail select</Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto">
      <div class="space-y-2">
        <h4 class="font-semibold">Main</h4>
        <div class="flex flex-nowrap gap-2 mt-3 items-center">
          <header class="w-12">Sail</header>
          <Button variant="outline" size="sm">Option 1</Button>
          <Button variant="outline" size="sm">Option 2</Button>
          <Button variant="outline" size="sm">Option 3</Button>
        </div>
        <div class="flex flex-nowrap gap-2 mt-3 items-center">
          <header class="w-12">Blade</header>
          <Button variant="outline" size="sm">Yes</Button>
          <Button variant="outline" size="sm">No</Button>
        </div>
        <div class="flex flex-nowrap gap-2 mt-3 items-center">
          <header class="w-12">Reefs</header>
          <Button variant="outline" size="sm">Reef 1</Button>
          <Button variant="outline" size="sm">Reef 2</Button>
          <Button variant="outline" size="sm">Reef 3</Button>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>
```

## Examples

### Simple Content

<div class="my-4 p-8 bg-muted flex justify-center">
  <Popover>
    <PopoverTrigger as-child>
      <Button>Show Info</Button>
    </PopoverTrigger>
    <PopoverContent>
      <div class="space-y-2">
        <h4 class="font-semibold">Information</h4>
        <p class="text-sm text-muted-foreground">
          This is a simple popover with text content.
        </p>
      </div>
    </PopoverContent>
  </Popover>
</div>

```vue
<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button>Show Info</Button>
    </PopoverTrigger>
    <PopoverContent>
      <div class="space-y-2">
        <h4 class="font-semibold">Information</h4>
        <p class="text-sm text-muted-foreground">
          This is a simple popover with text content.
        </p>
      </div>
    </PopoverContent>
  </Popover>
</template>
```

### With Actions

<div class="my-4 p-8 bg-muted flex justify-center">
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="secondary">Actions</Button>
    </PopoverTrigger>
    <PopoverContent>
      <div class="space-y-3">
        <h4 class="font-semibold">Quick Actions</h4>
        <div class="flex flex-col gap-2">
          <Button variant="ghost" size="sm" class="justify-start">Edit</Button>
          <Button variant="ghost" size="sm" class="justify-start">Duplicate</Button>
          <Button variant="ghost" size="sm" class="justify-start text-destructive">Delete</Button>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</div>

```vue
<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="secondary">Actions</Button>
    </PopoverTrigger>
    <PopoverContent>
      <div class="space-y-3">
        <h4 class="font-semibold">Quick Actions</h4>
        <div class="flex flex-col gap-2">
          <Button variant="ghost" size="sm" class="justify-start">Edit</Button>
          <Button variant="ghost" size="sm" class="justify-start">Duplicate</Button>
          <Button variant="ghost" size="sm" class="justify-start text-destructive">Delete</Button>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>
```

### Different Positions

<div class="my-4 p-8 bg-muted">
  <div class="flex flex-wrap gap-4 justify-center items-center min-h-[200px]">
    <Popover>
      <PopoverTrigger as-child>
        <Button variant="outline">Top</Button>
      </PopoverTrigger>
      <PopoverContent side="top">
        <p class="text-sm">Content positioned on top</p>
      </PopoverContent>
    </Popover>
    <Popover>
      <PopoverTrigger as-child>
        <Button variant="outline">Right</Button>
      </PopoverTrigger>
      <PopoverContent side="right">
        <p class="text-sm">Content positioned on right</p>
      </PopoverContent>
    </Popover>
    <Popover>
      <PopoverTrigger as-child>
        <Button variant="outline">Bottom</Button>
      </PopoverTrigger>
      <PopoverContent side="bottom">
        <p class="text-sm">Content positioned on bottom</p>
      </PopoverContent>
    </Popover>
    <Popover>
      <PopoverTrigger as-child>
        <Button variant="outline">Left</Button>
      </PopoverTrigger>
      <PopoverContent side="left">
        <p class="text-sm">Content positioned on left</p>
      </PopoverContent>
    </Popover>
  </div>
</div>

```vue
<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline">Top</Button>
    </PopoverTrigger>
    <PopoverContent side="top">
      <p class="text-sm">Content positioned on top</p>
    </PopoverContent>
  </Popover>

  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline">Right</Button>
    </PopoverTrigger>
    <PopoverContent side="right">
      <p class="text-sm">Content positioned on right</p>
    </PopoverContent>
  </Popover>

  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline">Bottom</Button>
    </PopoverTrigger>
    <PopoverContent side="bottom">
      <p class="text-sm">Content positioned on bottom</p>
    </PopoverContent>
  </Popover>

  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline">Left</Button>
    </PopoverTrigger>
    <PopoverContent side="left">
      <p class="text-sm">Content positioned on left</p>
    </PopoverContent>
  </Popover>
</template>
```

## API Reference

### Popover

The root component that manages the popover state.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | - | Controlled open state |
| `defaultOpen` | `boolean` | `false` | Default open state |
| `modal` | `boolean` | `false` | Whether the popover is modal |

### PopoverTrigger

The button or element that triggers the popover.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `as-child` | `boolean` | `false` | Merge props onto child element |

### PopoverContent

The content container for the popover.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `side` | `'top' \| 'right' \| 'bottom' \| 'left'` | `'bottom'` | Preferred side to render |
| `align` | `'start' \| 'center' \| 'end'` | `'center'` | Alignment relative to trigger |
| `sideOffset` | `number` | `4` | Distance from trigger |
| `alignOffset` | `number` | `0` | Offset along alignment axis |
| `avoidCollisions` | `boolean` | `true` | Prevent collisions with viewport |

## Usage Guidelines

### When to Use

- **Contextual Information**: Display additional details without cluttering the main interface
- **Quick Actions**: Provide access to actions related to a specific element
- **Form Controls**: Show advanced options or filters
- **Help Text**: Provide contextual help or tooltips with rich content

### When Not to Use

- **Critical Information**: Use modal dialogs for important messages that require user attention
- **Long Forms**: Use dedicated pages or dialogs for complex forms
- **Navigation Menus**: Consider using dropdown menus or navigation drawers for site navigation
- **Persistent Content**: Use cards or panels for content that should always be visible

## Accessibility

- Supports keyboard navigation with <kbd>Escape</kbd> to close
- Focus is managed automatically when opening and closing
- Supports `aria-label` and `aria-describedby` attributes
- Follows WAI-ARIA popover pattern
