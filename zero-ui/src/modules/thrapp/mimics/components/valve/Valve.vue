<script setup lang="ts">
import { computed, toRefs } from "vue";
import { ComponentOrientation, createSizeAndViewbox, getNextOrientation, useOrientation } from "..";
import {
  FlowValveProps,
  SwitchValveProps,
  ThreeWayValveProps,
  VALVE_BASE_ORIENTATION,
  VALVE_HEIGHT,
  VALVE_MARKER_COLOR,
  VALVE_MARKER_TEXT_COLOR,
  VALVE_PORT_COLORS,
  VALVE_STROKE_COLOR,
  VALVE_WIDTH,
  ValvePort,
  ValvePortColors,
  ValveProps,
  ValveType,
} from "./index";

const props = withDefaults(
  defineProps<
    | (ValveProps<ValveType.FlowControl> & FlowValveProps)
    | (ValveProps<ValveType.Switch> & SwitchValveProps)
    | (ValveProps<ValveType.ThreeWay> & ThreeWayValveProps)
  >(),
  {
    orientation: ComponentOrientation.Up,
    markerLabel: "E",
  },
);

const { orientation, state } = toRefs(props);

const portColors = computed<ValvePortColors>(() => VALVE_PORT_COLORS[props.state]);

const baseOrientation = computed<ComponentOrientation>(() => {
  if (state.value !== "closed") return VALVE_BASE_ORIENTATION;
  return getNextOrientation(VALVE_BASE_ORIENTATION);
});

const rotation = useOrientation(orientation, baseOrientation);
</script>

<template>
  <svg
    data-slot="flow-valve"
    v-bind="createSizeAndViewbox(VALVE_WIDTH, VALVE_HEIGHT)"
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
        :fill="portColors[ValvePort.Left]"
        class="transition-colors duration-300"
        :stroke="VALVE_STROKE_COLOR"
      />
      <path
        d="M18 18L30 10L30 26L18 18Z"
        :fill="portColors[ValvePort.Right]"
        class="transition-colors duration-300"
        :stroke="VALVE_STROKE_COLOR"
      />

      <path
        v-if="type === ValveType.ThreeWay"
        d="M18 18L10 30L26 30L18 18Z"
        :fill="portColors[ValvePort.Bottom]"
        class="transition-colors duration-300"
        :stroke="VALVE_STROKE_COLOR"
      />

      <circle
        cx="18"
        cy="18"
        r="2"
        :fill="VALVE_STROKE_COLOR"
      />

      <path
        d="M17.1992 12.3999H18.7992L18.7992 16.3999H17.1992L17.1992 12.3999Z"
        :fill="VALVE_STROKE_COLOR"
      />

      <g v-if="type === ValveType.FlowControl || type === ValveType.ThreeWay">
        <rect
          x="16.166"
          y="8.3999"
          width="4.57969"
          height="0.8"
          transform="rotate(45 16.166 8.3999)"
          :fill="VALVE_MARKER_COLOR"
        />
        <rect
          x="13.6992"
          y="8.8999"
          width="8.6"
          height="3"
          :stroke="VALVE_STROKE_COLOR"
        />
        <path
          d="M14.0852 13.6006L20.7996 6.59489L21.3653 7.16057L14.6508 14.1663L14.0852 13.6006Z"
          :fill="VALVE_MARKER_COLOR"
        />
        <path
          d="M22.5685 5.45466L21.9378 8.1948L19.8284 6.08542L22.5685 5.45466Z"
          :fill="VALVE_MARKER_COLOR"
        />
      </g>

      <g v-else-if="type === ValveType.Switch">
        <circle
          cx="18"
          cy="9.19995"
          r="3.5"
          :fill="VALVE_MARKER_COLOR"
          :stroke="VALVE_STROKE_COLOR"
        />
        <text
          x="18"
          y="11.2"
          :fill="VALVE_MARKER_TEXT_COLOR"
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
