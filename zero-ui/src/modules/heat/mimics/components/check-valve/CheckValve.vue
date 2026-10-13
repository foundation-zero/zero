<script setup lang="ts">
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  CHECK_VALVE_BASE_ORIENTATION,
  CHECK_VALVE_BODY_FILL,
  CHECK_VALVE_HEIGHT,
  CHECK_VALVE_MARK_COLOR,
  CHECK_VALVE_STROKE_COLOR,
  CHECK_VALVE_WIDTH,
} from "./index";

withDefaults(defineProps<MimicComponentBaseProps>(), {
  orientation: CHECK_VALVE_BASE_ORIENTATION,
});
</script>

<template>
  <MimicComponent
    :width="CHECK_VALVE_WIDTH"
    :height="CHECK_VALVE_HEIGHT"
    :base-orientation="CHECK_VALVE_BASE_ORIENTATION"
    :orientation="orientation"
    data-slot="check-valve"
  >
    <g transform="translate(4 0)">
      <rect
        x="0.5"
        y="6.5"
        width="23"
        height="15"
        :fill="CHECK_VALVE_BODY_FILL"
        :stroke="CHECK_VALVE_STROKE_COLOR"
      />
      <path
        d="M1 6.99982L23 20.9998"
        :stroke="CHECK_VALVE_STROKE_COLOR"
      />
      <path
        d="M5 1.40389L16.1972 1.40389V2.47659L5 2.47659V1.40389Z"
        :fill="CHECK_VALVE_MARK_COLOR"
      />
      <path
        d="M19 2L15.7524 4V0L19 2Z"
        :fill="CHECK_VALVE_MARK_COLOR"
      />
    </g>
  </MimicComponent>
</template>
