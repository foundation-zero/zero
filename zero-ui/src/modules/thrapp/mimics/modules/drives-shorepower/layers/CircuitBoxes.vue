<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, ["drives:shorepower"]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="938.63"
      y="235.41"
      width="196"
      height="212"
      inverted
      v-bind="circuits['drives:shorepower']"
    />
  </g>
</template>
