<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes, toRefs } from "vue";
import { CIRCUIT_BOX_BORDER_COLOR } from ".";
import { createMimicComponentContext, MimicComponentState } from "..";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    state?: MimicComponentState;
    width?: string | number;
  }>(),
  {
    width: 196,
    state: MimicComponentState.Normal,
  },
);

const { state } = toRefs(props);
const { stateColor, strokeWidth } = createMimicComponentContext(state);

const borderColor = computed(() => {
  if (state.value === MimicComponentState.Normal) {
    return CIRCUIT_BOX_BORDER_COLOR;
  } else {
    return stateColor.value;
  }
});
</script>

<template>
  <div :class="cn('flex gap-0.5', props.class)">
    <div
      class="w-3 rounded-tl-md rounded-bl-md transition-colors"
      :style="{ 'background-color': borderColor }"
    />
    <div
      class="bg-background pointer-events-none grow overflow-hidden rounded-tr-md rounded-br-md border border-dashed p-2 pb-1 transition-all"
      :style="{
        'border-color': borderColor,
        'border-width': strokeWidth + 'px',
      }"
    >
      <slot />
    </div>
  </div>
</template>
