<script setup lang="ts">
import { ClassValue } from "class-variance-authority/types";
import { StepSlider } from "../step-slider";

defineProps<{ class: ClassValue }>();
const position = defineModel<number>("position", { required: true });
</script>

<template>
  <StepSlider
    :model-value="[position]"
    :max="100"
    :min="0"
    class="aspect-[1/2] w-full max-w-[200px]"
    v-bind="{ class: $props.class }"
    :min-steps-between-thumbs="3"
    :steps="6"
    @update:model-value="(val) => (position = val?.[0] ?? 0)"
  />
  <div class="mt-3 inline-flex items-end">
    <span class="text-3xl font-bold md:text-4xl">
      <span>{{ Math.round(100 - position) }}</span>
    </span>
    <span class="ml-0.5 font-light">&percnt;</span>
  </div>
</template>
