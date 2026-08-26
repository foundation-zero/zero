<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes, toRefs } from "vue";

import { createMimicComponentContext, createSizeAndViewbox, MimicComponentState } from "..";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    width?: number | string;
    height?: number | string;
    forceHeight?: boolean;
    state?: MimicComponentState;
  }>(),
  { width: 200, height: 162, forceHeight: false },
);

const { state } = toRefs(props);
const { strokeWidth, stateColor } = createMimicComponentContext(state);
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(Number(width), Number(height), forceHeight)"
    class="fill-background transition-all"
  >
    <!-- Seperate foreignObject is needed to prevent the border from pushing the content inwards when
      state changes -->
    <foreignObject
      :width="width"
      :height="height"
    >
      <div
        :class="cn('bg-background h-full w-full transition-all', props.class)"
        :style="{
          'border-color': stateColor,
          'border-width': `${strokeWidth}px`,
        }"
      />
    </foreignObject>
    <foreignObject
      :width="width"
      :height="height"
    >
      <div :class="cn('h-full w-full p-2 pb-1', props.class)">
        <slot />
      </div>
    </foreignObject>
  </svg>
</template>
