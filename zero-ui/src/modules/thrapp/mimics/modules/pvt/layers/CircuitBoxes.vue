<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance } from "../../../instances";
import HotWaterCircuitInstance from "../../../instances/HotWaterCircuitInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const circuits = PVT_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const hotWaterCircuits = PVT_MIMIC_DATA[MimicComponentType.FreshwaterCircuit];
</script>

<template>
  <g>
    <HotWaterCircuitInstance
      x="885"
      y="15"
      force-height
      height="300"
      v-bind="hotWaterCircuits?.['pcm']"
    />

    <LoopCircuitInstance
      x="1093"
      y="347"
      width="194"
      height="168"
      force-height
      v-bind="circuits?.['seawater']"
    />
  </g>
</template>
