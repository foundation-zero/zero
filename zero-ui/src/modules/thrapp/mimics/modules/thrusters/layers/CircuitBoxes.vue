<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance } from "../../../instances";
import HotWaterCircuitInstance from "../../../instances/HotWaterCircuitInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const circuits = THRUSTERS_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const hotWaterCircuits = THRUSTERS_MIMIC_DATA[MimicComponentType.HotWaterCircuit];
</script>

<template>
  <g>
    <HotWaterCircuitInstance
      x="1002"
      y="316"
      force-height
      height="300"
      v-bind="hotWaterCircuits?.['pcm']"
    />

    <LoopCircuitInstance
      x="590"
      y="6"
      width="194"
      height="168"
      force-height
      v-bind="circuits?.['seawater']"
    />
  </g>
</template>
