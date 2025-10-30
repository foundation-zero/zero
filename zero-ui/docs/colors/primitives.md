# Primitives

<script setup>
import { ref, onMounted } from 'vue'

function getColorValue(colorName) {
  if (typeof window === 'undefined') return '' // SSR compatibility
  const computedStyle = getComputedStyle(document.documentElement)
  return computedStyle.getPropertyValue(`--color-${colorName}`).trim()
}
</script>

Primitive colors are the foundation of our color system. Each scale provides a range from light to dark variants.

## Neutral

<div class="mb-8">
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

## Neutral Grey

<div class="mb-8">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-0"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-0</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-0') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-50"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-50</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-50') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-100"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-100</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-100') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-200"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-200</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-200') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-300"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-300</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-300') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-400"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-400</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-400') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-500"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-500</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-500') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-600"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-600</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-600') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-700"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-700</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-700') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-800"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-800</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-800') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-900"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-900</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-900') }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-3 p-3 border rounded-lg">
      <div class="w-12 h-12 rounded-md border bg-neutral-grey-1000"></div>
      <div>
        <div class="font-mono text-sm font-medium">neutral-grey-1000</div>
        <div class="font-mono text-xs text-muted-foreground">
          {{ getColorValue('neutral-grey-1000') }}
        </div>
      </div>
    </div>
  </div>
</div>

## Brand

<div class="mb-8">
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

## Accent A

<div class="mb-8">
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

## Accent B

<div class="mb-8">
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

## Accent C

<div class="mb-8">
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