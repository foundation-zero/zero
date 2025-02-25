<script setup lang="ts">
defineProps<{ pending?: boolean; progress?: number }>();
</script>

<template>
  <div
    class="h-1 w-full overflow-hidden transition-all"
    :class="{ 'opacity-0': !pending, 'opacity-100': pending || progress }"
  >
    <div
      class="h-full bg-primary/100"
      :class="{ 'w-full origin-left-right animate-progress': pending }"
      :style="{ width: progress !== undefined ? `${progress}%` : undefined }"
    ></div>
  </div>
</template>

<style lang="css">
.progress {
  animation: progress 1s infinite linear;
}

.left-right {
  transform-origin: 0% 50%;
}

@keyframes progress {
  0% {
    transform: translateX(0) scaleX(0);
  }
  40% {
    transform: translateX(0) scaleX(0.4);
  }
  100% {
    transform: translateX(100%) scaleX(0.5);
  }
}
</style>
