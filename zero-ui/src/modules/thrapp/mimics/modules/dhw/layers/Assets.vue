<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import HeatPumpInstance from "../../../instances/HeatPumpInstance.vue";
import HVACInstance from "../../../instances/HVACInstance.vue";

const heatpumps = getTooltipContexts(MimicComponentType.HeatPump, ["1035"]);
const hvacs = getTooltipContexts(MimicComponentType.HVAC, ["41001001"]);
</script>

<template>
  <g>
    <HeatPumpInstance
      x="70"
      y="656"
      :width="200"
      :height="178"
      force-height
      v-bind="heatpumps['1035']"
    />

    <HVACInstance
      x="670"
      y="400"
      :width="150"
      :height="150"
      force-height
      v-bind="hvacs['41001001']"
    />
  </g>
</template>
