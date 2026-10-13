<script setup lang="ts">
import { HTMLAttributes } from "vue";

withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    width?: string | number;
    height?: string | number;
    x?: string | number;
    y?: string | number;
  }>(),
  {
    width: 196,
    height: 128,
  },
);
</script>

<template>
  <foreignObject v-bind="$props">
    <slot />
  </foreignObject>
</template>
