# Colors

A comprehensive color system with primitive and semantic color tokens that adapt to light and dark themes.

<script setup>
import { ref, onMounted } from 'vue'

function getColorValue(colorName) {
  if (typeof window === 'undefined') return '' // SSR compatibility
  const computedStyle = getComputedStyle(document.documentElement)
  return computedStyle.getPropertyValue(`--color-${colorName}`).trim()
}
</script>

## Overview

The Zero UI color system is built on a foundation of primitive color scales that are then mapped to semantic color tokens. This approach ensures consistent theming across light and dark modes while maintaining semantic meaning in component design.

## Primitive Colors

Primitive colors are the foundation of our color system. Each scale provides a range from light to dark variants.

### Neutral Scale

<div class="mb-8">
  <h4 class="text-lg font-semibold mb-4">Neutral Colors</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-0"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-0</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-0') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-50"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-50</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-50') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-100"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-100</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-100') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-200"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-200</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-200') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-300"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-300</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-300') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-400"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-400</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-400') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-500"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-500</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-500') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-600"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-600</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-600') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-700"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-700</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-700') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-800"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-800</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-800') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-900"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-900</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-900') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-1000"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-1000</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-1000') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Brand Scale

<div class="mb-8">
  <h4 class="text-lg font-semibold mb-4">Brand Colors</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-0"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-0</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-0') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-50"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-50</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-50') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-100"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-100</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-100') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-200"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-200</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-200') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-300"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-300</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-300') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-400"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-400</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-400') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-500"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-500</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-500') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-600"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-600</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-600') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-700"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-700</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-700') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-800"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-800</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-800') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-900"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-900</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-900') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-a-1000"></div>
      <div>
        <div class="font-mono text-sm font-medium">brand-a-1000</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('brand-a-1000') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Accent A Scale (Red)

<div class="mb-8">
  <h4 class="text-lg font-semibold mb-4">Accent A Colors (Red)</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-0"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-0</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-0') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-50"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-50</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-50') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-100"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-100</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-100') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-200"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-200</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-200') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-300"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-300</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-300') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-400"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-400</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-400') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-500"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-500</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-500') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-600"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-600</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-600') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-700"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-700</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-700') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-800"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-800</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-800') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-900"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-900</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-900') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-a-1000"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-a-1000</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-a-1000') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Accent B Scale (Yellow)

<div class="mb-8">
  <h4 class="text-lg font-semibold mb-4">Accent B Colors (Yellow)</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-0"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-0</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-0') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-50"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-50</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-50') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-100"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-100</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-100') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-200"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-200</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-200') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-300"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-300</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-300') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-400"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-400</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-400') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-500"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-500</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-500') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-600"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-600</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-600') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-700"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-700</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-700') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-800"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-800</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-800') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-900"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-900</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-900') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-b-1000"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-b-1000</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-b-1000') }}
        </div>
      </div>
    </div>
  </div>
</div>

### Accent C Scale (Green)

<div class="mb-8">
  <h4 class="text-lg font-semibold mb-4">Accent C Colors (Green)</h4>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-0"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-0</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-0') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-50"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-50</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-50') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-100"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-100</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-100') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-200"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-200</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-200') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-300"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-300</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-300') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-400"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-400</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-400') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-500"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-500</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-500') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-600"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-600</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-600') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-700"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-700</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-700') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-800"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-800</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-800') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-900"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-900</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-900') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-c-1000"></div>
      <div>
        <div class="font-mono text-sm font-medium">accent-c-1000</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('accent-c-1000') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Semantic Colors

Semantic colors are contextual colors that are mapped to specific use cases. They automatically adapt between light and dark themes.

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-background"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">background</div>
        <div class="text-xs text-muted-foreground">Primary background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('background') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-background-muted"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">background-muted</div>
        <div class="text-xs text-muted-foreground">Muted background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('background-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-background-inverse"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">background-inverse</div>
        <div class="text-xs text-muted-foreground">Inverse background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('background-inverse') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-background-subtle"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">background-subtle</div>
        <div class="text-xs text-muted-foreground">Subtle background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('background-subtle') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">foreground</div>
        <div class="text-xs text-muted-foreground">Primary text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-foreground-inverse"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">foreground-inverse</div>
        <div class="text-xs text-muted-foreground">Inverse text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('foreground-inverse') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-foreground-subtle"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">foreground-subtle</div>
        <div class="text-xs text-muted-foreground">Subtle text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('foreground-subtle') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-primary"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">primary</div>
        <div class="text-xs text-muted-foreground">Primary color for main actions</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('primary') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-primary-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">primary-foreground</div>
        <div class="text-xs text-muted-foreground">Text color for primary backgrounds</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('primary-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-secondary"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">secondary</div>
        <div class="text-xs text-muted-foreground">Secondary color for less prominent actions</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('secondary') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-secondary-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">secondary-foreground</div>
        <div class="text-xs text-muted-foreground">Text color for secondary backgrounds</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('secondary-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-muted"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">muted</div>
        <div class="text-xs text-muted-foreground">Muted background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-muted-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">muted-foreground</div>
        <div class="text-xs text-muted-foreground">Muted text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('muted-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">accent</div>
        <div class="text-xs text-muted-foreground">Accent color for highlights</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('accent') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-accent-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">accent-foreground</div>
        <div class="text-xs text-muted-foreground">Text color for accent backgrounds</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('accent-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-destructive"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">destructive</div>
        <div class="text-xs text-muted-foreground">Color for destructive actions (errors, delete)</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('destructive') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-destructive-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">destructive-foreground</div>
        <div class="text-xs text-muted-foreground">Text color for destructive backgrounds</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('destructive-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-constructive"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">constructive</div>
        <div class="text-xs text-muted-foreground">Color for constructive actions (success, save)</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('constructive') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-constructive-muted"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">constructive-muted</div>
        <div class="text-xs text-muted-foreground">Muted constructive color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('constructive-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-constructive-dull"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">constructive-dull</div>
        <div class="text-xs text-muted-foreground">Dull constructive color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('constructive-dull') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-warning"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">warning</div>
        <div class="text-xs text-muted-foreground">Color for warning states</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('warning') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-warning-muted"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">warning-muted</div>
        <div class="text-xs text-muted-foreground">Muted warning color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('warning-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-warning-dull"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">warning-dull</div>
        <div class="text-xs text-muted-foreground">Dull warning color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('warning-dull') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">brand</div>
        <div class="text-xs text-muted-foreground">Primary brand color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('brand') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-muted"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">brand-muted</div>
        <div class="text-xs text-muted-foreground">Muted brand color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('brand-muted') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-brand-dull"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">brand-dull</div>
        <div class="text-xs text-muted-foreground">Dull brand color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('brand-dull') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-border"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">border</div>
        <div class="text-xs text-muted-foreground">Default border color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-input"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">input</div>
        <div class="text-xs text-muted-foreground">Input background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('input') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-input-border"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">input-border</div>
        <div class="text-xs text-muted-foreground">Input border color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('input-border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-ring"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">ring</div>
        <div class="text-xs text-muted-foreground">Focus ring color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('ring') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-card"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">card</div>
        <div class="text-xs text-muted-foreground">Card background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('card') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-card-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">card-foreground</div>
        <div class="text-xs text-muted-foreground">Card text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('card-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-popover"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">popover</div>
        <div class="text-xs text-muted-foreground">Popover background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('popover') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-popover-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">popover-foreground</div>
        <div class="text-xs text-muted-foreground">Popover text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('popover-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-chart-1"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">chart-1</div>
        <div class="text-xs text-muted-foreground">Chart color 1</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('chart-1') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-chart-2"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">chart-2</div>
        <div class="text-xs text-muted-foreground">Chart color 2</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('chart-2') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-chart-3"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">chart-3</div>
        <div class="text-xs text-muted-foreground">Chart color 3</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('chart-3') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-chart-4"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">chart-4</div>
        <div class="text-xs text-muted-foreground">Chart color 4</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('chart-4') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-chart-5"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">chart-5</div>
        <div class="text-xs text-muted-foreground">Chart color 5</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('chart-5') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar</div>
        <div class="text-xs text-muted-foreground">Sidebar background color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-foreground</div>
        <div class="text-xs text-muted-foreground">Sidebar text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-primary"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-primary</div>
        <div class="text-xs text-muted-foreground">Sidebar primary color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-primary') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-primary-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-primary-foreground</div>
        <div class="text-xs text-muted-foreground">Sidebar primary text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-primary-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-accent"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-accent</div>
        <div class="text-xs text-muted-foreground">Sidebar accent color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-accent') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-accent-foreground"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-accent-foreground</div>
        <div class="text-xs text-muted-foreground">Sidebar accent text color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-accent-foreground') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-border"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-border</div>
        <div class="text-xs text-muted-foreground">Sidebar border color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-border') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-sidebar-ring"></div>
      <div class="flex-1">
        <div class="font-mono text-sm font-medium">sidebar-ring</div>
        <div class="text-xs text-muted-foreground">Sidebar ring color</div>
        <div class="font-mono text-xs text-muted-foreground mt-1">
          {{ getColorValue('sidebar-ring') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Usage

### CSS Custom Properties

All colors are available as CSS custom properties:

```css
/* Primitive colors */
background-color: var(--color-neutral-50);
color: var(--color-brand-a-600);

/* Semantic colors */
background-color: var(--color-background);
color: var(--color-foreground);
border-color: var(--color-border);
```

### Tailwind CSS Classes

Use Tailwind CSS utility classes with our custom color tokens:

```html
<!-- Background colors -->
<div class="bg-background text-foreground">Default background</div>
<div class="bg-primary text-primary-foreground">Primary background</div>

<!-- Primitive colors -->
<div class="bg-neutral-50 text-neutral-900">Neutral colors</div>
<div class="bg-brand-a-500 text-white">Brand colors</div>

<!-- Semantic colors -->
<div class="bg-destructive text-destructive-foreground">Error state</div>
<div class="bg-constructive text-white">Success state</div>
```

## Dark Mode

Dark mode is handled through CSS custom properties, but can be toggled using a @vueuse utility.

```javascript
import { useDark } from "@vueuse/core";

const isDark = useDark();
// Toggle dark mode
isDark.value = !isDark.value;

// Enable dark mode
isDark.value = true;

// Disable dark mode
isDark.value = false;
```

## Color Guidelines

### Accessibility

- Ensure sufficient contrast ratios (4.5:1 minimum for normal text, 3:1 for large text)
- Use semantic colors for consistent meaning across components
- Test color combinations in both light and dark modes

### Best Practices

- **Use semantic colors** for component styling rather than primitive colors when possible
- **Primitive colors** should be used for custom designs or when semantic colors don't fit
- **Brand colors** should be used sparingly and primarily for brand elements
- **Destructive colors** for errors, warnings, and destructive actions
- **Constructive colors** for success states and positive actions