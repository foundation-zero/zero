<script setup lang="ts">
defineProps<{ animationDelay: number; animationDuration: number }>();
</script>

<template>
  <p
    class="text-brand mb-4 text-sm font-semibold tracking-[0.35em] uppercase opacity-0 motion-reduce:animate-none motion-reduce:opacity-100"
    :style="{
      animationDelay: `${animationDelay}ms`,
      animationDuration: `${animationDuration}ms`,
    }"
  >
    <slot />
  </p>
</template>

<style scoped>
p {
  animation: rise-in cubic-bezier(0.18, 0.89, 0.32, 1.28) forwards;
}
</style>
