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
  @apply flex items-center whitespace-nowrap justify-between gap-2
  p-6 h-8 
  border-primary/5 transition-colors disabled:opacity-50 hover:bg-muted-foreground
  disabled:pointer-events-none
  text-base;

  &.selected {
    @apply font-bold;
  }

  &:not(.selected) {
    @apply font-light;
  }
}
</style>
