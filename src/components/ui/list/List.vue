<script setup lang="ts">
defineProps<{ orientation?: "horizontal" | "vertical"; size?: number }>();
</script>

<template>
  <ul
    class="list"
    :class="[orientation ?? 'vertical', `grid-cols-${size ?? 1}`]"
  >
    <slot />
  </ul>
</template>

<style lang="scss" scoped>
.list {
  @apply grid overflow-hidden rounded-xl border border-primary/10 bg-muted/80 hover:cursor-pointer;

  &.vertical {
    @apply divide-y;
  }

  &.horizontal {
    @apply divide-x;
  }
}
</style>
