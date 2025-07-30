<script setup lang="ts">
import { ratioAsPercentage } from "@/lib/utils";

defineProps<{ color?: string }>();
const level = defineModel<number>("level", { required: true });
const levelPercentage = ratioAsPercentage(level);
</script>

<template>
  <div
    class="aspect-[1/2] w-full max-w-[20px] overflow-hidden rounded-md bg-primary/20 md:max-w-[30px]"
  >
    <div
      :style="{ height: `${100 - levelPercentage}%` }"
      :class="[color ?? 'bg-primary/90']"
      class="w-full"
    />
  </div>
</template>
