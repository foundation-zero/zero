<script setup lang="ts">
import { getMimicComponentContext, MimicComponentState } from "../index.ts";
import { ACTUATED_VALVE_MARKER_COLOR } from "./index.ts";

const { stateColor, state } = getMimicComponentContext();
</script>

<template>
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
    :stroke="stateColor"
    :stroke-width="state !== MimicComponentState.Normal ? 2 : 1"
  />
  <path
    d="M14.0852 13.6006L20.7996 6.59489L21.3653 7.16057L14.6508 14.1663L14.0852 13.6006Z"
    :fill="ACTUATED_VALVE_MARKER_COLOR"
  />
  <path
    d="M22.5685 5.45466L21.9378 8.1948L19.8284 6.08542L22.5685 5.45466Z"
    :fill="ACTUATED_VALVE_MARKER_COLOR"
  />
</template>
