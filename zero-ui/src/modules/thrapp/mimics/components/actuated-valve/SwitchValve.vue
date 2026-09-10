<script setup lang="ts">
import { computed } from "vue";
import { ACTUATED_VALVE_MARKER_COLOR, ACTUATED_VALVE_MARKER_TEXT_COLOR } from ".";
import { getMimicComponentContext } from "..";

withDefaults(defineProps<{ fixedLabel?: boolean }>(), {
  fixedLabel: true,
});
const { stateColor, rotationDegrees } = getMimicComponentContext();

// The anchor travels with the rotated valve body while the glyph stays upright.
const counterRotationStyle = computed(() => ({
  transform: `rotate(${-rotationDegrees.value}deg)`,
  transformOrigin: `${18}px ${9.19995}px`,
}));
</script>

<template>
  <g
    class="transition-transform duration-300"
    :style="fixedLabel ? counterRotationStyle : undefined"
  >
    <circle
      cx="18"
      cy="9.19995"
      r="3.5"
      :fill="ACTUATED_VALVE_MARKER_COLOR"
      :stroke="stateColor"
    />
    <text
      x="18"
      y="11"
      :fill="ACTUATED_VALVE_MARKER_TEXT_COLOR"
      font-size="6"
      font-family="Inter, sans-serif"
      font-weight="400"
      text-anchor="middle"
    >
      <slot>E</slot>
    </text>
  </g>
</template>
