<script setup lang="ts">
import { computed } from "vue";
import { getMimicComponentContext } from "..";
import {
  MANUAL_VALVE_BORDER_COLOR,
  MANUAL_VALVE_MARK_COLOR,
  MANUAL_VALVE_PORT_FILL,
} from "./index";

const { rotationDegrees } = getMimicComponentContext();
const counterRotationStyle = computed(() => ({
  transform: `rotate(${-rotationDegrees.value}deg)`,
  transformOrigin: "18px 18px",
}));
</script>

<template>
  <g
    :style="counterRotationStyle"
    data-slot="manual-flow-marker"
  >
    <g transform="translate(4 4)">
      <circle
        cx="14"
        cy="14"
        r="2.5"
        :fill="MANUAL_VALVE_PORT_FILL"
        :stroke="MANUAL_VALVE_BORDER_COLOR"
      />
      <line
        y1="-0.5"
        x2="9.18376"
        y2="-0.5"
        transform="matrix(-0.707107 0.707107 0.707107 0.707107 16.7229 11.8167)"
        :stroke="MANUAL_VALVE_MARK_COLOR"
      />
      <path
        d="M15.991 10.4209L17.4149 11.8448L18.0225 9.81325L15.991 10.4209Z"
        :fill="MANUAL_VALVE_MARK_COLOR"
        :stroke="MANUAL_VALVE_MARK_COLOR"
      />
    </g>
  </g>
</template>
