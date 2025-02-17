<script setup lang="ts">
defineProps<{ color?: string }>();
const level = defineModel<number>("level", { required: true });
</script>

<template>
  <div
    class="aspect-[1/2] w-full max-w-[20px] overflow-hidden rounded-md bg-primary/20 md:max-w-[30px]"
  >
    <div
      :style="{ height: `${100 - level}%` }"
      :class="[color ?? 'bg-primary/90']"
      class="w-full"
    />
  </div>
</template>
