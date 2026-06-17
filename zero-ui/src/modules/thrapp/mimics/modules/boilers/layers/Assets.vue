<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import HeatPumpInstance from "../../../instances/HeatPumpInstance.vue";
import { BOILERS_MIMIC_DATA } from "../data";

const assets = BOILERS_MIMIC_DATA[MimicComponentType.Asset];
</script>

<template>
  <g>
    <HeatPumpInstance
      x="70"
      y="656"
      :width="200"
      :height="164"
      force-height
      v-bind="assets['1035']"
    />

    <HeatPumpInstance
      x="670"
      y="400"
      :width="150"
      :height="140"
      force-height
      v-bind="assets['41001001']"
    />
  </g>
</template>
