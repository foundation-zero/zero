<script setup lang="ts">
import { computed, toRefs } from "vue";
import { ComponentOrientation, MimicComponentBaseProps, getNextOrientation } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  PUMP_BASE_ORIENTATION,
  PUMP_CENTER_X,
  PUMP_CENTER_Y,
  PUMP_HEIGHT,
  PUMP_RADIUS,
  PUMP_STATE_COLORS,
  PUMP_WIDTH,
  PumpProps,
  PumpState,
} from "./index";

const props = withDefaults(defineProps<PumpProps & MimicComponentBaseProps>(), {
  state: PumpState.Active,
  orientation: PUMP_BASE_ORIENTATION,
});

const { state, orientation } = toRefs(props);

const colors = computed(() => PUMP_STATE_COLORS[state.value]);

const orientationWithRotation = computed<ComponentOrientation>(() => {
  if (state.value === PumpState.Transient) return getNextOrientation(orientation.value, -1);
  else if (state.value === PumpState.Closed) return getNextOrientation(orientation.value, -2);
  else return orientation.value;
});
</script>

<template>
  <MimicComponent
    :width="PUMP_WIDTH"
    :height="PUMP_HEIGHT"
    :base-orientation="PUMP_BASE_ORIENTATION"
    :orientation="orientationWithRotation"
    data-slot="pump"
  >
    <circle
      :cx="PUMP_CENTER_X"
      :cy="PUMP_CENTER_Y"
      :r="PUMP_RADIUS"
      :fill="colors.body"
      :stroke="colors.ring"
      class="transition-colors duration-300"
    />

    <path
      d="M12.00439 36.4922L12.00439 17.5078L43.6465 27L12.00439 36.4922Z"
      :fill="colors.blade"
      :stroke="colors.ring"
      class="transition-colors duration-300"
    />
  </MimicComponent>
</template>
