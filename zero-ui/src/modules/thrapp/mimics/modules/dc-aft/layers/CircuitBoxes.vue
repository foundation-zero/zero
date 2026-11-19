<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, ["dc:aft"]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="910"
      y="219"
      width="196"
      height="212"
      inverted
      v-bind="circuits['dc:aft']"
    />
  </g>
</template>
