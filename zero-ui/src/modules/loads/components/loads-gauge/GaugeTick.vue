<script setup lang="ts">
import { formatInt, mmath } from "@/modules/common/lib/utils";
import { TICK_LENGTH, TICK_RADIUS } from ".";

defineProps<{
  value: number;
  angle: number;
  x: number;
  y: number;
}>();
</script>

<template>
  <g :transform="`rotate(${mmath.normalizeDegrees(angle + 90)}, ${x}, ${y})`">
    <line
      :x1="x"
      :y1="y - TICK_LENGTH"
      :x2="x"
      :y2="y + TICK_LENGTH"
      class="stroke-neutral-grey-700"
      stroke-width="0.5"
    />
    <text
      :x="x"
      :y="y - TICK_RADIUS"
      class="fill-neutral-grey-500"
      font-size="1em"
      text-anchor="middle"
      dominant-baseline="hanging"
    >
      {{ formatInt(value) }}
    </text>
  </g>
</template>
