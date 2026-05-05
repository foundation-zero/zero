<script setup lang="ts">
import { computed, toRefs } from "vue";
import { ComponentOrientation, createSizeAndViewbox, getNextOrientation, useOrientation } from "..";
import {
  ACTUATED_VALVE_BASE_ORIENTATION,
  ACTUATED_VALVE_HEIGHT,
  ACTUATED_VALVE_MARKER_COLOR,
  ACTUATED_VALVE_MARKER_TEXT_COLOR,
  ACTUATED_VALVE_PORT_COLORS,
  ACTUATED_VALVE_STROKE_COLOR,
  ACTUATED_VALVE_WIDTH,
  ActuatedValvePort,
  ActuatedValvePortColors,
  ActuatedValveProps,
  ActuatedValveType,
  FlowValveProps,
  SwitchValveProps,
  ThreeWayValveProps,
} from "./index";

const props = withDefaults(
  defineProps<
    | (ActuatedValveProps<ActuatedValveType.FlowControl> & FlowValveProps)
    | (ActuatedValveProps<ActuatedValveType.Switch> & SwitchValveProps)
    | (ActuatedValveProps<ActuatedValveType.ThreeWay> & ThreeWayValveProps)
  >(),
  {
    orientation: ACTUATED_VALVE_BASE_ORIENTATION,
    markerLabel: "E",
  },
);

const { orientation, state } = toRefs(props);

const portColors = computed<ActuatedValvePortColors>(() => ACTUATED_VALVE_PORT_COLORS[props.state]);

const orientationWithRotation = computed<ComponentOrientation>(() => {
  if (state.value !== "closed") return orientation.value;
  return getNextOrientation(orientation.value, 2);
});

const rotation = useOrientation(orientationWithRotation, ACTUATED_VALVE_BASE_ORIENTATION);
</script>

<template>
  <svg
    data-slot="actuated-valve"
    v-bind="createSizeAndViewbox(ACTUATED_VALVE_WIDTH, ACTUATED_VALVE_HEIGHT)"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    aria-hidden="true"
  >
    <g
      :style="rotation"
      class="origin-center transition-transform duration-300"
    >
      <path
        d="M18 18L6 26L6 10L18 18Z"
        :fill="portColors[ActuatedValvePort.Left]"
        class="transition-colors duration-300"
        :stroke="ACTUATED_VALVE_STROKE_COLOR"
      />
      <path
        d="M18 18L30 10L30 26L18 18Z"
        :fill="portColors[ActuatedValvePort.Right]"
        class="transition-colors duration-300"
        :stroke="ACTUATED_VALVE_STROKE_COLOR"
      />

      <path
        v-if="type === ActuatedValveType.ThreeWay"
        d="M18 18L10 30L26 30L18 18Z"
        :fill="portColors[ActuatedValvePort.Bottom]"
        class="transition-colors duration-300"
        :stroke="ACTUATED_VALVE_STROKE_COLOR"
      />

      <circle
        cx="18"
        cy="18"
        r="2"
        :fill="ACTUATED_VALVE_STROKE_COLOR"
      />

      <path
        d="M17.1992 12.3999H18.7992L18.7992 16.3999H17.1992L17.1992 12.3999Z"
        :fill="ACTUATED_VALVE_STROKE_COLOR"
      />

      <g v-if="type === ActuatedValveType.FlowControl || type === ActuatedValveType.ThreeWay">
        <rect
          x="16.166"
          y="8.3999"
          width="4.57969"
          height="0.8"
          transform="rotate(45 16.166 8.3999)"
          :fill="ACTUATED_VALVE_MARKER_COLOR"
        />
        <rect
          x="13.6992"
          y="8.8999"
          width="8.6"
          height="3"
          :stroke="ACTUATED_VALVE_STROKE_COLOR"
        />
        <path
          d="M14.0852 13.6006L20.7996 6.59489L21.3653 7.16057L14.6508 14.1663L14.0852 13.6006Z"
          :fill="ACTUATED_VALVE_MARKER_COLOR"
        />
        <path
          d="M22.5685 5.45466L21.9378 8.1948L19.8284 6.08542L22.5685 5.45466Z"
          :fill="ACTUATED_VALVE_MARKER_COLOR"
        />
      </g>

      <g v-else-if="type === ActuatedValveType.Switch">
        <circle
          cx="18"
          cy="9.19995"
          r="3.5"
          :fill="ACTUATED_VALVE_MARKER_COLOR"
          :stroke="ACTUATED_VALVE_STROKE_COLOR"
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
          {{ markerLabel }}
        </text>
      </g>
    </g>
  </svg>
</template>
