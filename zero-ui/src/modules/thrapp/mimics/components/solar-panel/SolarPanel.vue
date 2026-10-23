<script setup lang="ts">
import { computed } from "vue";
import {
  SOLAR_PANEL_DIMENSIONS,
  SOLAR_PANEL_GRID,
  SolarPanelOrientation,
  SolarPanelProps,
  SolarPanelSize,
  solarYieldColor,
} from ".";

const props = withDefaults(
  defineProps<SolarPanelProps & { x?: number | string; y?: number | string }>(),
  {
    size: () => SolarPanelSize.Large,
    orientation: () => SolarPanelOrientation.Portrait,
    x: 0,
    y: 0,
    yieldRatio: undefined,
  },
);

const dimensions = computed(() => SOLAR_PANEL_DIMENSIONS[props.size]);
const grid = computed(() => SOLAR_PANEL_GRID[props.size]);
const isLandscape = computed(() => props.orientation === SolarPanelOrientation.Landscape);

// The panel is drawn in portrait and rotated a quarter turn clockwise for landscape.
const transform = computed(() =>
  isLandscape.value ? `translate(${dimensions.value.height} 0) rotate(90)` : undefined,
);
const yieldColor = computed(() =>
  props.yieldRatio === undefined ? undefined : solarYieldColor(props.yieldRatio),
);
</script>

<template>
  <svg
    :x="x"
    :y="y"
    :width="isLandscape ? dimensions.height : dimensions.width"
    :height="isLandscape ? dimensions.width : dimensions.height"
    overflow="visible"
    data-slot="solar-panel"
  >
    <g :transform="transform">
      <rect
        x="0.25"
        y="0.25"
        :width="dimensions.width - 0.5"
        :height="dimensions.height - 0.5"
        :fill="yieldColor"
        class="stroke-black/25 transition-colors duration-5000"
        stroke-width="0.5"
      />

      <g
        class="stroke-border-subtle"
        stroke-width="0.5"
        opacity="0.3"
      >
        <line
          v-for="column in grid.columns"
          :key="`c${column}`"
          :x1="column"
          :x2="column"
          y1="0.5"
          :y2="dimensions.height - 0.5"
        />
        <line
          v-for="row in grid.rows"
          :key="`r${row}`"
          x1="0.5"
          :x2="dimensions.width - 0.5"
          :y1="row"
          :y2="row"
        />
      </g>
    </g>
  </svg>
</template>
