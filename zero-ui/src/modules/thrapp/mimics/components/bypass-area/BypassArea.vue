<script setup lang="ts">
import { createSizeAndViewbox } from "..";

defineProps<{ width: number; height: number }>();
</script>

<template>
  <svg v-bind="createSizeAndViewbox(width, height)">
    <foreignObject
      width="100%"
      height="100%"
    >
      <div
        class="border-flows-pipe text-2xs bg-background/60 text-muted-foreground flex-col rounded-md border border-dashed p-1 text-center"
        :style="{
          height: `${height}px`,
          width: `${width}px`,
        }"
      >
        <slot />
      </div>
    </foreignObject>
  </svg>
</template>
