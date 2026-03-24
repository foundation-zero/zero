<script setup lang="ts">
defineProps<{
  letters: string[];
  animationDuration: number;
  animationInterval: number;
  animationDelay: number;
}>();
</script>

<template>
  <h1
    class="text-foreground text-[clamp(4rem,16vw,11rem)] leading-none font-black tracking-[0.18em] uppercase"
    :style="{
      animationDuration: `${animationDuration}ms`,
      animationDelay: `${animationDelay}ms`,
    }"
  >
    <span
      v-for="(letter, index) in letters"
      :key="letter"
      class="inline-block opacity-0 motion-reduce:transform-none motion-reduce:animate-none motion-reduce:opacity-100"
      :style="{ '--letter-delay': `${index * animationInterval}ms` }"
    >
      {{ letter }}
    </span>
  </h1>
</template>

<style scoped>
@keyframes zero-letter {
  from {
    opacity: 0;
    transform: translateY(1.25rem) scale(0.94);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

span {
  transform: translateY(1.25rem) scale(0.94);
  text-shadow: 0 0 30px color-mix(in srgb, var(--brand-dull) 24%, transparent);
  animation: zero-letter cubic-bezier(0.2, 1, 0.3, 1) forwards;
}
</style>
