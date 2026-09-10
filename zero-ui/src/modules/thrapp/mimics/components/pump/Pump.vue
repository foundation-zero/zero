<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentBaseProps, MimicComponentState } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  MANUAL_PUMP_COLORS,
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
  state: MimicComponentState.Normal,
  pumpState: PumpState.Active,
  orientation: PUMP_BASE_ORIENTATION,
  manual: false,
  width: PUMP_WIDTH,
  height: PUMP_HEIGHT,
});

const colors = computed(() =>
  props.manual
    ? MANUAL_PUMP_COLORS
    : PUMP_STATE_COLORS[props.state === MimicComponentState.Normal ? props.pumpState : props.state],
);
</script>

<template>
  <MimicComponent
    :width="props.width"
    :height="props.height"
    :viewBox="`0 0 ${PUMP_WIDTH} ${PUMP_HEIGHT}`"
    :base-orientation="PUMP_BASE_ORIENTATION"
    :orientation="orientation"
    :state="state"
    data-slot="pump"
  >
    <template #default="{ strokeWidth }">
      <circle
        :cx="PUMP_CENTER_X"
        :cy="PUMP_CENTER_Y"
        :r="PUMP_RADIUS"
        :fill="colors.body"
        :stroke="colors.ring"
        :stroke-width="strokeWidth"
        class="transition-all duration-300"
      />

      <path
        d="M12.00439 36.4922L12.00439 17.5078L43.6465 27L12.00439 36.4922Z"
        :fill="colors.blade"
        :stroke="colors.ring"
        :stroke-width="strokeWidth"
        class="transition-all duration-300"
      />
    </template>
  </MimicComponent>
</template>
