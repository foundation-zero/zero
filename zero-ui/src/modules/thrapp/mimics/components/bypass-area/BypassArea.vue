<script setup lang="ts">
import { createSizeAndViewbox } from "..";

defineProps<{ width: number; height: number }>();
</script>
<template>
  <svg v-bind="createSizeAndViewbox(width, height)">
    <rect
      :width="width"
      :height="height"
      rx="16"
      fill="rgba(244, 249, 254, 0.05)"
      stroke="#AA22BB"
      stroke-width="1.5"
      stroke-dasharray="3,3"
    />

    <rect
      x="0.5"
      y="0.5"
      :width="width - 1"
      :height="height - 1"
      rx="15.5"
      class="stroke-flows-pipe"
      stroke-opacity="0.55"
      stroke-dasharray="2 2"
    />

    <text
      y="16"
      height="30"
      :x="width / 2"
      class="text-2xs fill-muted-foreground"
      text-anchor="middle"
    >
      <slot />
    </text>
  </svg>
</template>
