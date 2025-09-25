# Semantic Colors

<script setup>
import { ref, onMounted } from 'vue'

function getColorValue(colorName) {
  if (typeof window === 'undefined') return '' // SSR compatibility
  const computedStyle = getComputedStyle(document.documentElement)
  return computedStyle.getPropertyValue(`--${colorName}`).trim()
}
</script>

Contextual colors that provide meaning and automatically adapt between light and dark themes. These colors are built on top of our [primitive color scales](./primitives.md) and provide consistent semantic meaning across the design system.

## Base Colors

Fundamental colors for backgrounds, text, and basic UI elements.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--background)"></div>
      <div>
        <div class="font-mono text-sm font-medium">background</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('background') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--muted-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">muted-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('muted-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--disabled)"></div>
      <div>
        <div class="font-mono text-sm font-medium">disabled</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('disabled') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--disabled-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">disabled-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('disabled-foreground') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Border Colors

Colors for borders, dividers, and separators.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--border)"></div>
      <div>
        <div class="font-mono text-sm font-medium">border</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--border-subtle)"></div>
      <div>
        <div class="font-mono text-sm font-medium">border-subtle</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('border-subtle') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Inverse Colors

Colors for high contrast elements and dark backgrounds.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--inverse)"></div>
      <div>
        <div class="font-mono text-sm font-medium">inverse</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('inverse') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--inverse-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">inverse-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('inverse-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--inverse-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">inverse-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('inverse-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--inverse-muted-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">inverse-muted-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('inverse-muted-foreground') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Interactive Colors

Colors for interactive elements like buttons, links, and focus states.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--primary)"></div>
      <div>
        <div class="font-mono text-sm font-medium">primary</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('primary') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--primary-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">primary-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('primary-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--secondary)"></div>
      <div>
        <div class="font-mono text-sm font-medium">secondary</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('secondary') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--secondary-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">secondary-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('secondary-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--accent)"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--accent-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--ring)"></div>
      <div>
        <div class="font-mono text-sm font-medium">ring</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('ring') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Brand Colors

Brand-specific colors for maintaining visual identity.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--brand)"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--brand-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--brand-dull)"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-dull</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-dull') }}
        </div>
      </div>
    </div>
  </div>
</div>

## State Colors

Colors that communicate different states and meanings.

### Constructive (Success)

Colors for positive states, success messages, and completed actions.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--constructive)"></div>
      <div>
        <div class="font-mono text-sm font-medium">constructive</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('constructive') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--constructive-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">constructive-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('constructive-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--constructive-dull)"></div>
      <div>
        <div class="font-mono text-sm font-medium">constructive-dull</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('constructive-dull') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Warning (Caution)

Colors for warning messages, caution states, and attention-needed situations.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--warning)"></div>
      <div>
        <div class="font-mono text-sm font-medium">warning</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('warning') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--warning-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">warning-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('warning-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--warning-dull)"></div>
      <div>
        <div class="font-mono text-sm font-medium">warning-dull</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('warning-dull') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Destructive (Error)

Colors for error states, destructive actions, and critical alerts.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--destructive)"></div>
      <div>
        <div class="font-mono text-sm font-medium">destructive</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('destructive') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--destructive-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">destructive-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('destructive-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--destructive-dull)"></div>
      <div>
        <div class="font-mono text-sm font-medium">destructive-dull</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('destructive-dull') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Attention (Info)

Colors for informational states, tips, and general attention-grabbing elements.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--attention)"></div>
      <div>
        <div class="font-mono text-sm font-medium">attention</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('attention') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--attention-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">attention-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('attention-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--attention-dull)"></div>
      <div>
        <div class="font-mono text-sm font-medium">attention-dull</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('attention-dull') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Usage

Semantic colors are used directly as CSS custom properties or through Tailwind utilities:

```css
/* CSS Custom Properties */
background: var(--background);
color: var(--foreground);
border-color: var(--border);

/* State colors */
color: var(--constructive);
background: var(--destructive-muted);
```

```html
<!-- Tailwind Classes -->
<div class="bg-background text-foreground border-border">
  Content with semantic colors
</div>

<button class="bg-primary text-primary-foreground">
  Primary Action
</button>

<div class="text-constructive border-constructive-muted">
  Success message
</div>
```

## Theme Adaptation

Semantic colors automatically adapt to different themes (light/dark) by referencing the appropriate primitive colors. This ensures consistent visual hierarchy and meaning across theme changes while maintaining accessibility standards.
