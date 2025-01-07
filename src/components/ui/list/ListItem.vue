<script setup lang="ts">
defineProps<{ selected?: boolean }>();
</script>

<template>
  <li
    :class="{
      selected,
    }"
  >
    <slot />
  </li>
</template>

<style lang="scss" scoped>
li {
  @apply flex h-8 items-center justify-between gap-2 whitespace-nowrap border-primary/5 p-6 text-base transition-colors hover:bg-muted-foreground disabled:pointer-events-none disabled:opacity-50;

  &.selected {
    @apply font-bold;
  }

  &:not(.selected) {
    @apply font-light;
  }
}
</style>
