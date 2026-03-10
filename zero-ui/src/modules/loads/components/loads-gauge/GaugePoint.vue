<script setup lang="ts">
import { generateRandomId } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { Colors, GAUGE_CENTER, POINT_ARC_RADIUS, POINT_RADIUS } from ".";

const props = withDefaults(
  defineProps<{
    cx: number;
    cy: number;
    r?: number;
    fill?: Colors;
  }>(),
  {
    r: () => POINT_RADIUS,
    fill: () => Colors.Empty,
  },
);

const SHADOW_OFFSET = 0.5;
const MASK_PADDING = 2;
const shadowMaskId = generateRandomId("gauge-point-mask");

// The shadow points toward the center of the gauge
const shadowOffset = computed(() => {
  const dx = props.cx - GAUGE_CENTER.x;
  const dy = props.cy - GAUGE_CENTER.y;

  return {
    x: (-dx / POINT_ARC_RADIUS) * SHADOW_OFFSET,
    y: (-dy / POINT_ARC_RADIUS) * SHADOW_OFFSET,
  };
});
</script>

<template>
  <g v-if="fill !== Colors.Transparent">
    <mask
      :id="shadowMaskId"
      maskUnits="userSpaceOnUse"
    >
      <!-- Create a mask that allows the shadow to show only outside the main circle. 
       Make the rect a little larger than the circle to ensure the shadow is fully visible.
      -->
      <rect
        :x="cx - r - MASK_PADDING"
        :y="cy - r - MASK_PADDING"
        :width="(r + MASK_PADDING) * 2"
        :height="(r + MASK_PADDING) * 2"
        fill="white"
      />
      <circle
        :cx="cx"
        :cy="cy"
        :r="r"
        fill="black"
      />
    </mask>

    <circle
      class="transition-all duration-150 ease-in-out"
      :cx="cx"
      :cy="cy"
      :r="r"
      :fill="fill"
    />

    <circle
      :cx="cx + shadowOffset.x"
      :cy="cy + shadowOffset.y"
      :r="r"
      class="fill-neutral-0/15"
      :mask="`url(#${shadowMaskId})`"
    />
  </g>
</template>
