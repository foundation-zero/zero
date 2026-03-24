<script setup lang="ts">
defineProps<{
  to: string;
  animationDelay: number;
  animationDuration: number;
}>();
</script>

<template>
  <RouterLink
    :to="to"
    data-slot="tile"
    class="group text-decoration-none relative min-h-80 text-inherit no-underline opacity-0"
    :style="{
      animationDelay: `${animationDelay}ms`,
      animationDuration: `${animationDuration}ms`,
    }"
  >
    <slot />
  </RouterLink>
</template>

<style scoped>
[data-slot="tile"] {
  animation: rise-in cubic-bezier(0.18, 0.89, 0.32, 1.28) forwards;
}

@media (prefers-reduced-motion: reduce) {
  [data-slot="tile"] {
    animation: none;
    opacity: 1;
  }
}
</style>
