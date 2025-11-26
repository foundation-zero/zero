<script setup lang="ts">
import { ratioAsPercentage } from "@common/lib/utils";

import { StepSlider } from "@common/components/step-slider";
import { computed, HTMLAttributes } from "vue";
import { getContext } from ".";

defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { value, commit, disabled, editable } = getContext();

const levelPercentage = ratioAsPercentage(value);
const blindsPosition = computed({
  get() {
    return [levelPercentage.value ?? 0];
  },
  set([val]: number[]) {
    levelPercentage.value = Math.round(val ?? 0);
  },
});
</script>

<template>
  <StepSlider
    v-model:model-value="blindsPosition"
    :max="100"
    :min="0"
    class="aspect-1/2 w-full max-w-[200px]"
    :class="{ 'opacity-50': disabled }"
    v-bind="{ class: $props.class }"
    :min-steps-between-thumbs="3"
    :disabled="disabled"
    :steps="6"
    :hide-thumb="!editable"
    @dragend="commit()"
    @touchend="commit()"
    @click="commit()"
  />
</template>
