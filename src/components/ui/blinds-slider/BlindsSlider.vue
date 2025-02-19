<script setup lang="ts">
import { ratioAsPercentage } from "@/lib/utils";
import { ClassValue } from "class-variance-authority/types";
import { computed } from "vue";
import { StepSlider } from "../step-slider";

defineProps<{ class: ClassValue }>();
const level = defineModel<number>("level", { required: true });
const levelPercentage = ratioAsPercentage(level);
const blindsPosition = computed({
  get() {
    return [Math.round(100 - (levelPercentage.value ?? 0))];
  },
  set([val]: number[]) {
    levelPercentage.value = Math.round(100 - (val ?? 0));
  },
});
</script>

<template>
  <StepSlider
    v-model:model-value="blindsPosition"
    :max="100"
    :min="0"
    class="aspect-[1/2] w-full max-w-[200px]"
    v-bind="{ class: $props.class }"
    :min-steps-between-thumbs="3"
    :steps="6"
  />
  <div class="mt-3 inline-flex items-center">
    <span class="text-3xl font-extrabold md:text-4xl">
      <span>{{ blindsPosition ?? 0 }}</span>
    </span>
    <span class="mx-1.5 text-3xl md:text-4xl">/</span>
    <span class="text-xl font-extralight md:text-2xl">100</span>
  </div>
</template>
