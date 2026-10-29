<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import ThrusterInstance from "../../../instances/ThrusterInstance.vue";

const thrusters = getTooltipContexts(MimicComponentType.Thruster, ["15001001", "15001002"]);
</script>

<template>
  <g>
    <ThrusterInstance
      x="-24"
      y="162"
      v-bind="thrusters['15001001']"
    />

    <ThrusterInstance
      x="-24"
      y="413"
      v-bind="thrusters['15001002']"
    />
  </g>
</template>
