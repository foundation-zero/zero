<script setup lang="ts">
import { cn, ratioAsPercentage } from "@/modules/common/lib/utils";
import { computed, type HTMLAttributes } from "vue";
import { getTrackContext } from ".";
import { VariableState } from "../../types";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  value?: number;
  state: VariableState;
}>();

const { type } = getTrackContext();

const position = computed(() => {
  if (props.value === undefined) {
    return 0;
  } else if (type.value === "symmetric") {
    return (props.value + 1) / 2;
  } else {
    return props.value;
  }
});

const positionAsPercentage = ratioAsPercentage(position);
</script>

<template>
  <div
    data-slot="position-slider-thumb"
    :style="{ left: `${positionAsPercentage}%` }"
    :class="
      cn('bg-primary absolute -my-1 h-full border-l transition-all duration-200', props.class, {
        'border-warning': state === VariableState.Warning,
        'border-destructive': state === VariableState.Alarm,
        'border-foreground': state === VariableState.Neutral || state === VariableState.Unknown,
      })
    "
  >
    <svg
      data-slot="position-slider-thumb-pointer"
      class="absolute bottom-0 left-[-0.5px] -translate-x-1/2 translate-y-1/2"
      xmlns="http://www.w3.org/2000/svg"
      width="9"
      height="8"
      viewBox="0 0 9 8"
      fill="none"
    >
      <path
        d="M3.6273 0.5C4.01517 -0.166667 4.98483 -0.166667 5.3727 0.5L8.86349 6.5C9.25136 7.16667 8.76652 8 7.99079 8H1.00921C0.233477 8 -0.251356 7.16667 0.13651 6.5L3.6273 0.5Z"
        fill="#F4F9FE"
      />
    </svg>
  </div>
</template>
