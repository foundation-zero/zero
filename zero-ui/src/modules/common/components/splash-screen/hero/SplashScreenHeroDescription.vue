<script setup lang="ts">
defineProps<{ animationDelay: number; animationDuration: number }>();
</script>

<template>
  <p
    class="text-muted-foreground mx-auto mt-6 max-w-2xl text-base leading-7 text-balance opacity-0 motion-reduce:animate-none motion-reduce:opacity-100 sm:text-lg"
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
