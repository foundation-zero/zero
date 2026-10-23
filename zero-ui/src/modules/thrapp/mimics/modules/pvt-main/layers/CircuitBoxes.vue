<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, ["pvt:main"]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="1384"
      y="232.5"
      width="196"
      height="188"
      v-bind="circuits['pvt:main']"
    />
  </g>
</template>
