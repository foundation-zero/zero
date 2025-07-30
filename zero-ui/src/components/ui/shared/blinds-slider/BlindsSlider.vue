<script setup lang="ts">
import { ratioAsPercentage } from "@/lib/utils";

import { StepSlider } from "@components/shadcn/step-slider";
import { computed, HTMLAttributes, ref, watch } from "vue";

defineProps<{ class: HTMLAttributes["class"]; disabled?: boolean }>();
const level = defineModel<number>("level", { required: true });
const targetLevel = ref(level.value);

watch(level, (newLevel) => {
  targetLevel.value = newLevel;
});

const levelPercentage = ratioAsPercentage(targetLevel);
const blindsPosition = computed({
  get() {
    return [levelPercentage.value ?? 0];
  },
  set([val]: number[]) {
    levelPercentage.value = Math.round(val ?? 0);
  },
});

const commit = () => (level.value = targetLevel.value);
</script>

<template>
  <div class="flex w-full flex-col items-center">
    <StepSlider
      v-model:model-value="blindsPosition"
      :max="100"
      :min="0"
      class="aspect-[1/2] w-full max-w-[200px]"
      :class="{ 'opacity-50': disabled }"
      v-bind="{ class: $props.class }"
      :min-steps-between-thumbs="3"
      :disabled="disabled"
      :steps="6"
      @touchend.stop.prevent="commit()"
      @click.stop.prevent="commit()"
    />
    <div class="mt-3 inline-flex items-center">
      <span
        class="text-3xl font-extrabold md:text-4xl"
        data-testid="blindsPosition"
      >
        <span>{{ blindsPosition[0] ?? 0 }}</span>
      </span>
      <span class="mx-1.5 text-3xl md:text-4xl">/</span>
      <span class="text-xl font-extralight md:text-2xl">100</span>
    </div>
  </div>
</template>
