<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, ["pvt:owners"]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="851"
      y="213.5"
      width="196"
      height="240"
      v-bind="circuits['pvt:owners']"
    />
  </g>
</template>
