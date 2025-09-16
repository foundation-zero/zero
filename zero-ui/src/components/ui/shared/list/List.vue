<script setup lang="ts">
defineProps<{ orientation?: "horizontal" | "vertical"; size?: number }>();
</script>

<template>
  <ul
    class="border-primary/10 bg-background grid overflow-hidden rounded-md border hover:cursor-pointer"
    :class="[
      { 'divide-y': orientation === 'vertical', 'divide-x': orientation !== 'vertical' },
      `grid-cols-${size ?? 1}`,
    ]"
  >
    <slot />
  </ul>
</template>
