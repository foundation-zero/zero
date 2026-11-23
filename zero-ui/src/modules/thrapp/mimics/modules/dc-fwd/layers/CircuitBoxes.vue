<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, ["dc:fwd"]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="906"
      y="203"
      width="196"
      height="212"
      inverted
      v-bind="circuits['dc:fwd']"
    />
  </g>
</template>
