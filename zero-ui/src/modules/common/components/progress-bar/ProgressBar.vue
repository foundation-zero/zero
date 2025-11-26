<script setup lang="ts">
defineProps<{ pending?: boolean; progress?: number }>();
</script>

<template>
  <div
    class="h-1 w-full overflow-hidden transition-all"
    :class="{ 'opacity-0': !pending, 'opacity-100': pending || progress }"
  >
    <div
      class="bg-primary h-full"
      :class="{ 'left-right animate-progress w-full origin-[0%_50%]': pending }"
      :style="{ width: progress !== undefined ? `${progress}%` : undefined }"
    ></div>
  </div>
</template>
