<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance, SeawaterCircuitInstance } from "../../../instances";

const seaWaterCircuits = getTooltipContexts(MimicComponentType.SeawaterCircuit, [
  "thrusters:seawater",
]);
const connectingCircuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, [
  "thrusters:pcm",
]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="1002"
      y="316"
      force-height
      height="195"
      v-bind="connectingCircuits['thrusters:pcm']"
    />

    <SeawaterCircuitInstance
      x="595"
      y="20"
      width="194"
      height="85"
      force-height
      v-bind="seaWaterCircuits['thrusters:seawater']"
    />
  </g>
</template>
