<script setup lang="ts">
import { HTMLAttributes } from "vue";
import { createSizeAndViewbox } from "../index.ts";

withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    width?: string | number;
    height?: string | number;
    forceHeight?: boolean;
  }>(),
  {
    width: 196,
    height: 128,
    forceHeight: false,
  },
);
</script>

<template>
  <svg v-bind="createSizeAndViewbox(width, height, forceHeight)">
    <foreignObject
      :width="width"
      :height="height"
    >
      <slot />
    </foreignObject>
  </svg>
</template>
