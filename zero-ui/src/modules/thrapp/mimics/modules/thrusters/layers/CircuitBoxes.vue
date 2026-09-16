<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ExchangeCircuitInstance } from "../../../instances";
import ConnectingCircuitInstance from "../../../instances/ConnectingCircuitInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const circuits = THRUSTERS_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const connectingCircuits = THRUSTERS_MIMIC_DATA[MimicComponentType.ConnectingCircuit];
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="1002"
      y="316"
      force-height
      height="260"
      v-bind="connectingCircuits?.['pcm']"
    />

    <ExchangeCircuitInstance
      x="590"
      y="6"
      width="194"
      height="130"
      force-height
      v-bind="circuits?.['seawater']"
    />
  </g>
</template>
