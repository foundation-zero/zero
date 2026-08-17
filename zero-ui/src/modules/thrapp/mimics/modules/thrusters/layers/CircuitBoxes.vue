<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance } from "../../../instances";
import FreshwaterCircuitInstance from "../../../instances/FreshwaterCircuitInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const circuits = THRUSTERS_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const freshwaterCircuits = THRUSTERS_MIMIC_DATA[MimicComponentType.FreshwaterCircuit];
</script>

<template>
  <g>
    <FreshwaterCircuitInstance
      x="1002"
      y="316"
      force-height
      height="300"
      v-bind="freshwaterCircuits?.['pcm']"
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
