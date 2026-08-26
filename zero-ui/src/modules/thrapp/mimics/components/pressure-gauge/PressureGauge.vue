<script setup lang="ts">
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  PRESSURE_GAUGE_BASE_ORIENTATION,
  PRESSURE_GAUGE_BODY_FILL,
  PRESSURE_GAUGE_HEIGHT,
  PRESSURE_GAUGE_MARK_COLOR,
  PRESSURE_GAUGE_STROKE_COLOR,
  PRESSURE_GAUGE_WIDTH,
} from "./index";

withDefaults(defineProps<MimicComponentBaseProps>(), {
  orientation: PRESSURE_GAUGE_BASE_ORIENTATION,
});
</script>

<template>
  <MimicComponent
    :width="PRESSURE_GAUGE_WIDTH"
    :height="PRESSURE_GAUGE_HEIGHT"
    :base-orientation="PRESSURE_GAUGE_BASE_ORIENTATION"
    :orientation="orientation"
    :state="state"
    data-slot="pressure-gauge"
    class="fill-muted"
  >
    <g transform="translate(4 1)">
      <rect
        x="0.5"
        y="0.5"
        width="23"
        height="23"
        rx="11.5"
        :fill="PRESSURE_GAUGE_BODY_FILL"
        :stroke="PRESSURE_GAUGE_STROKE_COLOR"
      />
      <path
        d="M7.00744 16.2404L16.3289 6.9189L17.036 7.626L7.71455 16.9475L7.00744 16.2404Z"
        :fill="PRESSURE_GAUGE_MARK_COLOR"
      />
      <path
        d="M17.6342 6.39954L17.8954 8.775L15.2587 6.13828L17.6342 6.39954Z"
        :fill="PRESSURE_GAUGE_MARK_COLOR"
      />
      <path
        d="M12 24L12 30"
        :stroke="PRESSURE_GAUGE_STROKE_COLOR"
      />
    </g>
  </MimicComponent>
</template>
