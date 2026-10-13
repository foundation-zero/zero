<script setup lang="ts">
import {
  DHW_TANK_HEIGHT,
  DHW_TANK_LEVEL_LINE_OFFSET,
  DHW_TANK_LEVEL_WAVE_HEIGHT,
  DHW_TANK_WIDTH,
} from ".";
import { createSizeAndViewbox } from "..";
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(DHW_TANK_WIDTH, DHW_TANK_HEIGHT + DHW_TANK_LEVEL_WAVE_HEIGHT)"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <mask id="boiler-wave-mask">
        <g fill="white">
          <path
            d="M0 3.46597C36.7321 -4.85573 67.0831 3.49696 96.6172 10.8205C128.801 18.801 160.937 25.9264 204 13.215V115.001H124.43C117.212 116.099 109.706 116.68 102 116.68C94.2939 116.68 86.7876 116.099 79.5703 115.001H0V3.46597Z"
          />
          <rect
            width="100%"
            :height="DHW_TANK_HEIGHT"
            :y="DHW_TANK_LEVEL_WAVE_HEIGHT"
          />
        </g>
      </mask>
    </defs>
    <rect
      width="100%"
      class="fill-brand-a-500"
      :height="DHW_TANK_HEIGHT + DHW_TANK_LEVEL_WAVE_HEIGHT"
      mask="url(#boiler-wave-mask)"
      fill-opacity="0.25"
    />
    <line
      x1="0"
      x2="100%"
      :y1="DHW_TANK_LEVEL_LINE_OFFSET"
      :y2="DHW_TANK_LEVEL_LINE_OFFSET"
      class="stroke-cooling-medium"
      stroke-dasharray="2 2"
    />
  </svg>
</template>
