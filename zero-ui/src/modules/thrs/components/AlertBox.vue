<script setup lang="ts">
import { TriangleAlert } from "lucide-vue-next";
</script>

<template>
  <div
    class="text-muted-foreground border-border-subtle flex items-center gap-4 rounded-md border p-4 lg:gap-6 lg:p-6"
  >
    <TriangleAlert
      stroke-width="2"
      class="text-warning"
    />
    <slot />
  </div>
</template>
