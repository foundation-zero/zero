# Typography

The Zero UI typography system is built on two primary fonts with a comprehensive scale of sizes and carefully crafted type hierarchy.

<script setup>
import { ref, onMounted } from 'vue'

// Standard text sizes
const standardSizes = [
  { class: 'text-5xs', size: '0.25rem', lineHeight: '0.375rem', name: '5xs' },
  { class: 'text-4xs', size: '0.375rem', lineHeight: '0.625rem', name: '4xs' },
  { class: 'text-3xs', size: '0.5rem', lineHeight: '0.75rem', name: '3xs' },
  { class: 'text-2xs', size: '0.625rem', lineHeight: '1rem', name: '2xs' },
  { class: 'text-xs', size: '0.75rem', lineHeight: '1rem', name: 'xs' },
  { class: 'text-sm', size: '0.875rem', lineHeight: '1.25rem', name: 'sm' },
  { class: 'text-base', size: '1rem', lineHeight: '1.5rem', name: 'base' },
  { class: 'text-lg', size: '1.125rem', lineHeight: '1.75rem', name: 'lg' },
  { class: 'text-xl', size: '1.25rem', lineHeight: '1.75rem', name: 'xl' },
  { class: 'text-2xl', size: '1.5rem', lineHeight: '2rem', name: '2xl' },
  { class: 'text-3xl', size: '1.875rem', lineHeight: '2.25rem', name: '3xl' },
  { class: 'text-4xl', size: '2.25rem', lineHeight: '2.5rem', name: '4xl' },
  { class: 'text-5xl', size: '3rem', lineHeight: '1', name: '5xl' },
  { class: 'text-6xl', size: '3.75rem', lineHeight: '1', name: '6xl' }
]

// Relative text sizes (em-based)
const relativeSizes = [
  { class: 'text-r4xs', size: '0.375em', lineHeight: '0.625em', name: 'r4xs' },
  { class: 'text-r3xs', size: '0.5em', lineHeight: '0.75em', name: 'r3xs' },
  { class: 'text-r2xs', size: '0.625em', lineHeight: '1em', name: 'r2xs' },
  { class: 'text-rxs', size: '0.75em', lineHeight: '1em', name: 'rxs' },
  { class: 'text-rsm', size: '0.875em', lineHeight: '1.25em', name: 'rsm' },
  { class: 'text-rbase', size: '1em', lineHeight: '1.5em', name: 'rbase' },
  { class: 'text-rlg', size: '1.125em', lineHeight: '1.75em', name: 'rlg' },
  { class: 'text-rxl', size: '1.25em', lineHeight: '1.75em', name: 'rxl' },
  { class: 'text-r2xl', size: '1.5em', lineHeight: '2em', name: 'r2xl' },
  { class: 'text-r3xl', size: '1.875em', lineHeight: '2.25em', name: 'r3xl' },
  { class: 'text-r4xl', size: '2.25em', lineHeight: '2.5em', name: 'r4xl' },
  { class: 'text-r5xl', size: '3em', lineHeight: '1', name: 'r5xl' },
  { class: 'text-r6xl', size: '3.75em', lineHeight: '1', name: 'r6xl' }
]

// Font weights
const fontWeights = [
  { class: 'font-thin', weight: '100', name: 'Thin' },
  { class: 'font-extralight', weight: '200', name: 'Extra Light' },
  { class: 'font-light', weight: '300', name: 'Light' },
  { class: 'font-normal', weight: '400', name: 'Normal' },
  { class: 'font-medium', weight: '500', name: 'Medium' },
  { class: 'font-semibold', weight: '600', name: 'Semibold' },
  { class: 'font-bold', weight: '700', name: 'Bold' },
  { class: 'font-extrabold', weight: '800', name: 'Extra Bold' },
  { class: 'font-black', weight: '900', name: 'Black' }
]
</script>

## Overview

Zero UI's typography system provides a comprehensive set of text sizes, font families, and weights to create consistent and hierarchical text layouts across your application.

## Font Families

### Inter (Default)
The primary font family for body text, user interface elements, and general content.

<div class="my-4 p-4 border rounded-lg">
  <p class="text-lg mb-2" style="font-family: Inter, sans-serif">
    Inter Regular - ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890
  </p>
  <p class="text-lg font-medium mb-2" style="font-family: Inter, sans-serif">
    Inter Medium - The quick brown fox jumps over the lazy dog
  </p>
  <p class="text-lg font-bold" style="font-family: Inter, sans-serif">
    Inter Bold - Typography enhances readability and user experience
  </p>
</div>

### Urbanist (Headers)
Used for headings, headers, and display text to create visual hierarchy.

<div class="my-4 p-4 border rounded-lg">
  <p class="text-lg mb-2" style="font-family: Urbanist, sans-serif">
    Urbanist Regular - ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890
  </p>
  <p class="text-lg font-medium mb-2" style="font-family: Urbanist, sans-serif">
    Urbanist Medium - The quick brown fox jumps over the lazy dog
  </p>
  <p class="text-lg font-bold" style="font-family: Urbanist, sans-serif">
    Urbanist Bold - Beautiful headers and display text
  </p>
</div>

## Heading Hierarchy

### HTML Headings
All heading elements use Urbanist font family by default.

<div class="my-8 space-y-4">
  <div class="border-l-4 border-brand pl-4">
    <h1 class="mb-2">Heading 1 - Main Page Title</h1>
    <code class="text-sm text-muted-foreground">&lt;h1&gt;</code>
  </div>
  
  <div class="border-l-4 border-brand-muted pl-4">
    <h2 class="mb-2">Heading 2 - Section Title</h2>
    <code class="text-sm text-muted-foreground">&lt;h2&gt;</code>
  </div>
  
  <div class="border-l-4 border-brand-dull pl-4">
    <h3 class="mb-2">Heading 3 - Subsection Title</h3>
    <code class="text-sm text-muted-foreground">&lt;h3&gt;</code>
  </div>
  
  <div class="border-l-4 border-accent-a-400 pl-4">
    <h4 class="mb-2">Heading 4 - Component Title</h4>
    <code class="text-sm text-muted-foreground">&lt;h4&gt;</code>
  </div>
  
  <div class="border-l-4 border-accent-a-300 pl-4">
    <h5 class="mb-2">Heading 5 - Minor Heading</h5>
    <code class="text-sm text-muted-foreground">&lt;h5&gt;</code>
  </div>
  
  <div class="border-l-4 border-accent-a-200 pl-4">
    <h6 class="mb-2">Heading 6 - Smallest Heading</h6>
    <code class="text-sm text-muted-foreground">&lt;h6&gt;</code>
  </div>
</div>

## Text Sizes

### Standard Sizes (rem-based)
Fixed sizes that maintain consistent scale across all contexts.

<div class="space-y-3 my-6">
  <div v-for="size in standardSizes" :key="size.name" class="flex items-center gap-4 p-3 border rounded-lg">
    <div class="w-16 text-sm font-mono text-muted-foreground">{{ size.name }}</div>
    <div :class="size.class" class="flex-1">
      The quick brown fox jumps over the lazy dog
    </div>
    <div class="text-xs text-muted-foreground font-mono">
      {{ size.size }} / {{ size.lineHeight }}
    </div>
    <code class="text-xs bg-muted px-2 py-1 rounded">{{ size.class }}</code>
  </div>
</div>

### Relative Sizes (em-based)
Sizes that scale relative to the parent element's font size.

<div class="space-y-3 my-6">
  <div v-for="size in relativeSizes" :key="size.name" class="flex items-center gap-4 p-3 border rounded-lg">
    <div class="w-16 text-sm font-mono text-muted-foreground">{{ size.name }}</div>
    <div :class="size.class" class="flex-1">
      Relative text scales with context
    </div>
    <div class="text-xs text-muted-foreground font-mono">
      {{ size.size }} / {{ size.lineHeight }}
    </div>
    <code class="text-xs bg-muted px-2 py-1 rounded">{{ size.class }}</code>
  </div>
</div>

## Font Weights

Our variable fonts support a full range of weights from 100 to 900.

<div class="space-y-3 my-6">
  <div v-for="weight in fontWeights" :key="weight.name" class="flex items-center gap-4 p-3 border rounded-lg">
    <div class="w-24 text-sm font-mono text-muted-foreground">{{ weight.name }}</div>
    <div :class="weight.class" class="flex-1 text-lg">
      The quick brown fox jumps over the lazy dog
    </div>
    <div class="text-xs text-muted-foreground font-mono">{{ weight.weight }}</div>
    <code class="text-xs bg-muted px-2 py-1 rounded">{{ weight.class }}</code>
  </div>
</div>

## Typography Examples

### Article Layout

<div class="my-8 p-6 border rounded-lg max-w-none">
  <header class="mb-6">
    <h1 class="text-4xl font-bold mb-2">Design System Typography</h1>
    <p class="text-lg text-muted-foreground">Building consistent and accessible text hierarchy</p>
  </header>
  
  <h2>Introduction to Typography</h2>
  
  <p class="text-base leading-relaxed">
    Typography is the foundation of good design. It helps establish hierarchy, 
    improve readability, and create visual consistency across your application. 
    Our typography system provides the tools you need to create beautiful, 
    accessible text layouts.
  </p>
  
  <h3>Design Principles</h3>
  
  <p class="text-base leading-relaxed">
    Our typography follows these core principles:
  </p>
  
  <ul class="space-y-2">
    <li><strong>Hierarchy:</strong> Clear distinction between different levels of content</li>
    <li><strong>Readability:</strong> Optimized line heights and spacing for easy reading</li>
    <li><strong>Consistency:</strong> Uniform scaling and spacing across all text elements</li>
    <li><strong>Accessibility:</strong> Sufficient contrast and responsive sizing</li>
  </ul>
  
  <h4>Implementation Details</h4>
  
  <p class="text-sm text-muted-foreground">
    All typography classes are built using CSS custom properties and Tailwind's 
    utility system, ensuring consistency and easy maintenance.
  </p>
</div>

## Usage Guidelines

### CSS Custom Properties

All typography sizes are available as CSS custom properties:

```css
/* Standard sizes */
font-size: var(--text-lg);
line-height: var(--text-lg--line-height);

/* Relative sizes */
font-size: var(--text-rxl);
line-height: var(--text-rxl--line-height);
```

### Tailwind CSS Classes

Use Tailwind utility classes for consistent typography:

```html
<!-- Text sizes -->
<p class="text-base">Default body text</p>
<h2 class="text-2xl font-bold">Section heading</h2>
<small class="text-sm text-muted-foreground">Helper text</small>

<!-- Font weights -->
<span class="font-medium">Medium weight</span>
<strong class="font-semibold">Semibold text</strong>

<!-- Relative sizes -->
<span class="text-rxl">Scales with parent context</span>
```

### Component Usage

```vue
<template>
  <div>
    <!-- Header with Urbanist font -->
    <h1 class="text-3xl font-bold mb-4">Page Title</h1>
    
    <!-- Body text with Inter font -->
    <p class="text-base leading-relaxed mb-4">
      This paragraph uses the default Inter font for optimal readability
      in body text and user interface elements.
    </p>
    
    <!-- Small helper text -->
    <p class="text-sm text-muted-foreground">
      Additional information in smaller text
    </p>
  </div>
</template>
```

## Best Practices

### Typography Hierarchy

- **H1**: Page titles and main headings (`text-3xl` or `text-4xl`)
- **H2**: Section headings (`text-2xl` or `text-3xl`)
- **H3**: Subsection headings (`text-xl` or `text-2xl`)
- **H4-H6**: Component and minor headings (`text-lg` to `text-xl`)
- **Body**: Primary content (`text-base`)
- **Small**: Helper text and metadata (`text-sm` or `text-xs`)

### Font Family Selection

- **Use Urbanist** for headings, titles, and display text
- **Use Inter** for body text, UI elements, and data
- **Maintain consistency** within each content type

### Responsive Typography

- Use relative sizes (`text-r*`) when text should scale with context
- Use fixed sizes (`text-*`) for consistent UI elements
- Consider readability on different screen sizes

### Accessibility

- Maintain sufficient contrast ratios for all text
- Use semantic HTML headings for proper document structure
- Ensure text remains readable when zoomed to 200%
- Provide adequate line spacing for comfortable reading