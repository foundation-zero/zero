<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, type HTMLAttributes } from "vue";
import { MastLockState } from "../../types";
import { IndicatorLight } from "../indicator-light";

const props = defineProps<{
  state?: MastLockState;
  class?: HTMLAttributes["class"];
}>();

const variant = computed(() => {
  if (props.state === "error") return "destructive";
  if (props.state === true) return "constructive";
  return "neutral";
});
</script>

<template>
  <div
    data-slot="mast-lock-position"
    :class="cn('flex flex-row items-center gap-2', props.class)"
  >
    <IndicatorLight
      class="size-4 p-0.5"
      :variant="variant"
    />

    <span
      class="text-sm font-medium transition-colors duration-250"
      :class="{ 'text-disabled-foreground': !state, 'text-foreground': state }"
    >
      <slot />
    </span>
  </div>
</template>
