<script setup lang="ts">
import { Slider } from "@/components/ui/shadcn/slider";
defineProps<{ disabled?: boolean }>();
defineModel<boolean>("on", { required: true });
const brightness = defineModel<number>("brightness", { required: true });
</script>

<template>
  <Slider
    :min="0"
    :max="100"
    :model-value="[on ? brightness : 0]"
    :class="{ 'opacity-55': !on, 'opacity-30': disabled }"
    :disabled="disabled"
    @update:model-value="(val) => (brightness = val?.[0] ?? 0)"
  />
</template>
