<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance } from "../../../instances";
import { DRIVES_EXCHANGE_CIRCUIT_DATA } from "../data";

const exchangeCircuits = DRIVES_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <LoopCircuitInstance
    x="1314"
    y="19.916"
    :width="196"
    :height="220"
    force-height
    v-bind="exchangeCircuits.domesticHotWater"
  />
</template>
