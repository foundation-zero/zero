<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, [
  "pvt:main-fwd",
  "pvt:main-aft",
]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="1384"
      y="108.88"
      width="196"
      height="184.25"
      inverted
      v-bind="circuits['pvt:main-fwd']"
    />
    <ConnectingCircuitInstance
      x="1384"
      y="315.38"
      width="196"
      height="184.25"
      inverted
      v-bind="circuits['pvt:main-aft']"
    />
  </g>
</template>
