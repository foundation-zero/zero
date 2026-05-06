<script setup lang="ts">
import MimicComponent from "../MimicComponent.vue";
import {
  MANUAL_VALVE_BASE_ORIENTATION,
  MANUAL_VALVE_BORDER_COLOR,
  MANUAL_VALVE_HEIGHT,
  MANUAL_VALVE_MARK_COLOR,
  MANUAL_VALVE_PIVOT_BORDER_COLOR,
  MANUAL_VALVE_PORT_FILL,
  MANUAL_VALVE_WIDTH,
  ManualValveProps,
  ManualValveType,
} from "./index";

withDefaults(defineProps<ManualValveProps>(), {
  orientation: MANUAL_VALVE_BASE_ORIENTATION,
});
</script>

<template>
  <MimicComponent
    :width="MANUAL_VALVE_WIDTH"
    :height="MANUAL_VALVE_HEIGHT"
    :base-orientation="MANUAL_VALVE_BASE_ORIENTATION"
    :orientation="orientation"
    data-slot="manual-valve"
  >
    <path
      d="M18 18L6 26L6 10L18 18Z"
      :fill="MANUAL_VALVE_PORT_FILL"
      :stroke="MANUAL_VALVE_BORDER_COLOR"
    />
    <path
      d="M18 18L30 10L30 26L18 18Z"
      :fill="MANUAL_VALVE_PORT_FILL"
      :stroke="MANUAL_VALVE_BORDER_COLOR"
    />
    <path
      v-if="type === ManualValveType.ThreeWay"
      d="M18 18L26 30L10 30L18 18Z"
      :fill="MANUAL_VALVE_PORT_FILL"
      :stroke="MANUAL_VALVE_BORDER_COLOR"
    />

    <g v-if="type === ManualValveType.Switch || type === ManualValveType.ThreeWay">
      <circle
        cx="18"
        cy="18"
        r="3.5"
        :fill="MANUAL_VALVE_PORT_FILL"
        :stroke="MANUAL_VALVE_PIVOT_BORDER_COLOR"
      />
      <circle
        cx="18"
        cy="18"
        r="0.5"
        :fill="MANUAL_VALVE_MARK_COLOR"
      />
    </g>

    <g v-else-if="type === ManualValveType.FlowControl">
      <circle
        cx="18"
        cy="18"
        r="2.5"
        :fill="MANUAL_VALVE_PORT_FILL"
        :stroke="MANUAL_VALVE_BORDER_COLOR"
      />
      <path
        d="M13.8232 21.8232L13.6464 22L14 22.3536L14.1768 22.1768L14 22L13.8232 21.8232ZM22 14L19.2116 14.7471L21.2529 16.7884L22 14ZM14 22L14.1768 22.1768L20.5858 15.7678L20.409 15.591L20.2322 15.4142L13.8232 21.8232L14 22Z"
        :fill="MANUAL_VALVE_MARK_COLOR"
      />
    </g>
  </MimicComponent>
</template>
