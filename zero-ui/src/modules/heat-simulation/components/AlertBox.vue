<script setup lang="ts">
import { RiAlertLine } from "@remixicon/vue";
</script>

<template>
  <div
    class="text-muted-foreground border-border-subtle flex items-center gap-4 rounded-md border p-4 lg:gap-6 lg:p-6"
  >
    <RiAlertLine
      stroke-width="2"
      class="text-warning"
    />
    <slot />
  </div>
</template>
