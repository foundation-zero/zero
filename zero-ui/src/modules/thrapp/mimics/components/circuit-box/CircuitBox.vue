<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes, toRefs } from "vue";
import { CIRCUIT_BOX_BORDER_COLOR } from ".";
import { createMimicComponentContext, createSizeAndViewbox, MimicComponentState } from "..";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    width?: string | number;
    height?: string | number;
    forceHeight?: boolean;
    state?: MimicComponentState;
  }>(),
  {
    width: 196,
    height: 128,
    forceHeight: false,
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
  <svg v-bind="createSizeAndViewbox(width, height, forceHeight)">
    <foreignObject
      width="100%"
      height="100%"
    >
      <div :class="cn('flex w-full gap-0.5', props.class)">
        <div
          class="w-3 rounded-tl-md rounded-bl-md transition-colors"
          :style="{ 'background-color': borderColor }"
        />
        <div class="relative grow p-2 pb-1">
          <div
            class="bg-background pointer-events-none absolute top-0 left-0 h-full w-full grow rounded-tr-md rounded-br-md border border-dashed transition-all"
            :style="{ 'border-color': borderColor, 'border-width': strokeWidth + 'px' }"
          />
          <div class="relative">
            <slot />
          </div>
        </div>
      </div>
    </foreignObject>
  </svg>
</template>
