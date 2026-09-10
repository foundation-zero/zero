<script setup lang="ts">
import { computed } from "vue";
import {
  ACTUATED_VALVE_MARKER_TEXT_COLOR,
  VALVE_LEG_LABEL_BACKGROUND_COLOR,
  VALVE_LEG_LABEL_FONT_SIZE,
  VALVE_LEG_LABEL_HEIGHT,
  ValveLegLabelProps,
} from ".";
import { getMimicComponentContext } from "..";

const props = defineProps<ValveLegLabelProps>();

const { rotationDegrees } = getMimicComponentContext();

// The anchor travels with the rotated valve body while the glyph stays upright.
const counterRotationStyle = computed(() => ({
  transform: `rotate(${-rotationDegrees.value}deg)`,
  transformOrigin: `${props.x}px ${props.y}px`,
}));
</script>

<template>
  <g
    :style="counterRotationStyle"
    class="transition-transform duration-300"
  >
    <rect
      :x="x - width / 2"
      :y="y - VALVE_LEG_LABEL_HEIGHT / 2"
      :width="width"
      :height="VALVE_LEG_LABEL_HEIGHT"
      :fill="VALVE_LEG_LABEL_BACKGROUND_COLOR"
    />
    <text
      :x="x"
      :y="y"
      :fill="ACTUATED_VALVE_MARKER_TEXT_COLOR"
      :font-size="VALVE_LEG_LABEL_FONT_SIZE"
      font-family="Inter, sans-serif"
      font-weight="400"
      text-anchor="middle"
      dominant-baseline="central"
    >
      <slot />
    </text>
  </g>
</template>
