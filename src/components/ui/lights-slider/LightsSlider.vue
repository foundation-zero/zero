<script setup lang="ts">
import { Slider } from "../slider";
defineModel<boolean>("on", { required: true });
const brightness = defineModel<number>("brightness", { required: true });
</script>

<template>
  <Slider
    :disabled="!on"
    :min="0"
    :max="100"
    :model-value="[on ? brightness : 0]"
    :class="{ 'opacity-50': !on }"
    @update:model-value="(val) => (brightness = val?.[0] ?? 0)"
  />
</template>
