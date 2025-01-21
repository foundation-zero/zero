<script setup lang="ts">
defineProps<{ color?: string }>();
const position = defineModel<number>("position", { required: true });
</script>

<template>
  <div
    class="aspect-[1/6] w-full max-w-[10px] overflow-hidden rounded-md bg-primary/20 md:max-w-[15px]"
  >
    <div
      :style="{ height: `${100 - position}%` }"
      :class="[color ?? 'bg-primary/90']"
      class="w-full"
    />
  </div>
</template>
