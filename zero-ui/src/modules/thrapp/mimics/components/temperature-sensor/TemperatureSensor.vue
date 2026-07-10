<script setup lang="ts">
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  TEMPERATURE_SENSOR_BASE_ORIENTATION,
  TEMPERATURE_SENSOR_BODY_FILL,
  TEMPERATURE_SENSOR_HEIGHT,
  TEMPERATURE_SENSOR_MARK_COLOR,
  TEMPERATURE_SENSOR_WIDTH,
} from "./index";

withDefaults(defineProps<MimicComponentBaseProps>(), {
  orientation: TEMPERATURE_SENSOR_BASE_ORIENTATION,
});
</script>

<template>
  <MimicComponent
    :width="TEMPERATURE_SENSOR_WIDTH"
    :height="TEMPERATURE_SENSOR_HEIGHT"
    :base-orientation="TEMPERATURE_SENSOR_BASE_ORIENTATION"
    :orientation="orientation"
    data-slot="temperature-sensor"
    class="fill-muted"
    :state="state"
  >
    <template #default="{ stateColor, strokeWidth }">
      <!-- Center 24x30 source geometry in a 32x32 canvas to prevent clipping on 90deg rotations. -->
      <g transform="translate(4 0.75)">
        <rect
          x="0.5"
          y="0.5"
          width="23"
          height="23"
          :fill="TEMPERATURE_SENSOR_BODY_FILL"
          :stroke="stateColor"
          :stroke-width="strokeWidth"
        />

        <path
          d="M16.4693 15.228H17.2043L17.2078 18H17.9358L17.9323 15.228H18.4888V14.5H17.9323L17.9358 13.401H17.2078L17.2043 14.5H16.4693V15.228Z"
          :fill="TEMPERATURE_SENSOR_MARK_COLOR"
        />
        <path
          d="M7.36271 11V5.75H6.63471V11H7.36271Z"
          :fill="TEMPERATURE_SENSOR_MARK_COLOR"
        />

        <path
          d="M23.5 0.5L0.5 23.5"
          :stroke="stateColor"
          :stroke-width="strokeWidth"
        />
        <path
          d="M12 24L12 30"
          :stroke="stateColor"
          :stroke-width="strokeWidth"
        />
      </g>
    </template>
  </MimicComponent>
</template>
