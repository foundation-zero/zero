<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

import { createSizeAndViewbox } from "..";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    width?: number | string;
    height?: number | string;
    forceHeight?: boolean;
  }>(),
  { width: 200, height: 162, forceHeight: false },
);
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(width, height, forceHeight)"
    class="fill-background"
  >
    <foreignObject
      width="100%"
      height="100%"
    >
      <div
        :class="cn('border-constructive bg-background h-full w-full border p-2 pb-1', props.class)"
      >
        <slot />
      </div>
    </foreignObject>
  </svg>
</template>
