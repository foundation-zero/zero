<script setup lang="ts">
import { ACTUATED_VALVE_MARKER_COLOR, ACTUATED_VALVE_MARKER_TEXT_COLOR } from ".";
import { getMimicComponentContext } from "..";

const { stateColor } = getMimicComponentContext();
</script>

<template>
  <circle
    cx="18"
    cy="9.19995"
    r="3.5"
    :fill="ACTUATED_VALVE_MARKER_COLOR"
    :stroke="stateColor"
  />
  <text
    x="18"
    y="11.2"
    :fill="ACTUATED_VALVE_MARKER_TEXT_COLOR"
    font-size="6"
    font-family="Inter, sans-serif"
    font-weight="400"
    text-anchor="middle"
  >
    <slot>E</slot>
  </text>
</template>
