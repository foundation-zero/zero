# DHW Module

Documentation page for the DhwModule mimic composition.

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue'

const DhwModule = defineAsyncComponent(
  () => import('@/modules/thrapp/mimics/modules/dhw/DhwModule.vue'),
)

const isExpanded = ref(false)
</script>

## Overview

`DhwModule` will contain the full boiler-area mimic composition, including all relevant component instances and connecting piping for this module.

## Scope (Planned)

- Actuated and manual valve instances
- Pumps, exchangers, and sensor instances
- Pressure gauges and other module indicators
- Piping paths that connect all relevant equipment

## Preview

<ClientOnly>
  <div
    class="my-6 p-4 bg-muted rounded-md overflow-auto cursor-zoom-in"
    title="Click to expand"
    @click="isExpanded = true"
  >
    <DhwModule />
  </div>

  <Teleport to="body">
    <div
      v-if="isExpanded"
      style="position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.85);display:flex;align-items:center;justify-content:center;padding:1rem;"
      @click.self="isExpanded = false"
    >
      <div style="position:relative;width:100%;max-height:100vh;overflow:auto;background:var(--vp-c-bg);border-radius:0.5rem;padding:1rem;">
        <button
          style="position:absolute;top:0.75rem;right:0.75rem;z-index:1;padding:0.25rem 0.75rem;border-radius:0.25rem;background:var(--vp-c-bg-soft);border:1px solid var(--vp-c-divider);cursor:pointer;font-size:0.875rem;"
          @click="isExpanded = false"
        >✕ Close</button>
        <DhwModule />
      </div>
    </div>
  </Teleport>

<template #fallback>

<p class="text-sm text-muted-foreground">Loading module preview...</p>
</template>
</ClientOnly>

## Notes

This page is intentionally introduced early as a stable reference point while the module composition is iteratively expanded.
