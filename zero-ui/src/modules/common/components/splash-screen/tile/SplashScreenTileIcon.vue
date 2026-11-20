<script setup lang="ts">
import type { Component } from "vue";

defineProps<{
  icon: Component;
  background: string;
}>();
</script>

<template>
  <div
    data-slot="icon"
    class="relative flex h-[5.25rem] w-[5.25rem] items-center justify-center rounded-[1.5rem]"
    :style="{
      '--tile-icon-bg': background,
    }"
  >
    <component
      :is="icon"
      class="h-11 w-11 stroke-1"
    />
    <div class="absolute -top-2 -right-2">
      <slot />
    </div>
  </div>
</template>

<style scoped>
[data-slot="icon"] {
  background: color-mix(in srgb, var(--tile-icon-bg) 72%, transparent);
  box-shadow: inset 0 1px 0 color-mix(in srgb, white 28%, transparent);
}
</style>
