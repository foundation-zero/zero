<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import HeatPumpInstance from "../../../instances/HeatPumpInstance.vue";
import HVACInstance from "../../../instances/HVACInstance.vue";
import { DHW_MIMIC_DATA } from "../data/index.ts";

const heatpumps = DHW_MIMIC_DATA[MimicComponentType.HeatPump];
const hvacs = DHW_MIMIC_DATA[MimicComponentType.HVAC];
</script>

<template>
  <g>
    <HeatPumpInstance
      x="70"
      y="656"
      :width="200"
      :height="164"
      force-height
      v-bind="heatpumps['1035']"
    />

    <HVACInstance
      x="670"
      y="400"
      :width="150"
      :height="140"
      force-height
      v-bind="hvacs['41001001']"
    />
  </g>
</template>
