<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    color?: string;
    centerColor?: string;
    mix?: string;
    fadeStop?: string;
    animated?: boolean;
    animationDuration?: string;
    animationDelay?: string;
  }>(),
  {
    mix: "42%",
    fadeStop: "68%",
    animated: true,
    animationDuration: "12s",
    animationDelay: "0s",
  },
);

const orbCenterColor = computed(() => {
  if (props.centerColor) return props.centerColor;
  if (props.color) return `color-mix(in srgb, ${props.color} ${props.mix}, transparent)`;
  return "transparent";
});
</script>

<template>
  <div
    class="pointer-events-none absolute rounded-full motion-reduce:animate-none"
    :class="{ 'is-animated': props.animated }"
    :style="{
      '--orb-center-color': orbCenterColor,
      '--orb-fade-stop': props.fadeStop,
      animationDuration: props.animationDuration,
      animationDelay: props.animationDelay,
    }"
  />
</template>

<style scoped>
div {
  background: radial-gradient(circle, var(--orb-center-color) 0%, transparent var(--orb-fade-stop));
}

.is-animated {
  animation: float-orb ease-in-out infinite;
}

@keyframes float-orb {
  0%,
  100% {
    transform: translate(0, 0);
  }
  33% {
    transform: translate(30px, -30px);
  }
  66% {
    transform: translate(-20px, 20px);
  }
}
</style>
