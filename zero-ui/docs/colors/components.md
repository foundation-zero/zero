# Component Colors

<script setup>
import { ref, onMounted } from 'vue'

function getColorValue(colorName) {
  if (typeof window === 'undefined') return '' // SSR compatibility
  const computedStyle = getComputedStyle(document.documentElement)
  return computedStyle.getPropertyValue(`--${colorName}`).trim()
}
</script>

Specialized colors for specific UI components and contexts. These colors are designed for particular use cases and components, providing consistent styling across the design system while maintaining semantic meaning and accessibility.

## Input Colors

Specialized colors for form inputs and interactive fields.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--input)"></div>
      <div>
        <div class="font-mono text-sm font-medium">input</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('input') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--input-border)"></div>
      <div>
        <div class="font-mono text-sm font-medium">input-border</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('input-border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--input-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">input-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('input-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--input-muted)"></div>
      <div>
        <div class="font-mono text-sm font-medium">input-muted</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('input-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--input-muted-border)"></div>
      <div>
        <div class="font-mono text-sm font-medium">input-muted-border</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('input-muted-border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--input-muted-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">input-muted-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('input-muted-foreground') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Button Colors

Colors specifically for button components and their various states.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--button-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">button-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('button-foreground') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Card Colors

Colors for card components and container elements.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--card)"></div>
      <div>
        <div class="font-mono text-sm font-medium">card</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('card') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--card-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">card-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('card-foreground') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Popover Colors

Colors for popover, dropdown, and overlay components.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--popover)"></div>
      <div>
        <div class="font-mono text-sm font-medium">popover</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('popover') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--popover-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">popover-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('popover-foreground') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Sidebar Colors

Colors for navigation sidebars and menu components.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-primary)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-primary</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-primary') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-primary-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-primary-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-primary-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-accent)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-accent</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-accent') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-accent-foreground)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-accent-foreground</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-accent-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-border)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-border</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--sidebar-ring)"></div>
      <div>
        <div class="font-mono text-sm font-medium">sidebar-ring</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('sidebar-ring') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Chart Colors

A set of distinct colors for data visualization and charts.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--chart-1)"></div>
      <div>
        <div class="font-mono text-sm font-medium">chart-1</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('chart-1') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--chart-2)"></div>
      <div>
        <div class="font-mono text-sm font-medium">chart-2</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('chart-2') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--chart-3)"></div>
      <div>
        <div class="font-mono text-sm font-medium">chart-3</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('chart-3') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--chart-4)"></div>
      <div>
        <div class="font-mono text-sm font-medium">chart-4</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('chart-4') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border" style="background: var(--chart-5)"></div>
      <div>
        <div class="font-mono text-sm font-medium">chart-5</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('chart-5') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Usage

Component colors are designed for specific UI elements and provide consistent styling:

```css
/* Input styling */
.input {
  background: var(--input);
  border: 1px solid var(--input-border);
  color: var(--input-foreground);
}

.input:disabled {
  background: var(--input-muted);
  border-color: var(--input-muted-border);
  color: var(--input-muted-foreground);
}

/* Card styling */
.card {
  background: var(--card);
  color: var(--card-foreground);
}

/* Popover styling */
.popover {
  background: var(--popover);
  color: var(--popover-foreground);
}

/* Chart data series */
.chart-series-1 { fill: var(--chart-1); }
.chart-series-2 { fill: var(--chart-2); }
.chart-series-3 { fill: var(--chart-3); }
```

```html
<!-- Component examples -->
<input class="bg-input border-input-border text-input-foreground" />
<div class="bg-card text-card-foreground">Card content</div>
<div class="bg-popover text-popover-foreground">Dropdown menu</div>
```

## Design Principles

Component colors follow these design principles:

- **Context-Specific**: Each color is optimized for its intended component use case
- **Accessibility**: All component colors maintain proper contrast ratios
- **Theme Adaptable**: Colors automatically adjust for light and dark themes
- **Semantic Clarity**: Color names clearly indicate their intended usage
- **Consistent Hierarchy**: Related components share logical color relationships

These specialized colors ensure that components maintain visual consistency while providing the flexibility needed for complex UI patterns and interactions.