<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ExchangeCircuitInstance, SeawaterCircuitInstance } from "../../../instances";

const seawaterCircuits = getTooltipContexts(MimicComponentType.SeawaterCircuit, [
  "drives:seawater",
]);
const exchangeCircuits = getTooltipContexts(MimicComponentType.ExchangeCircuit, [
  "drives:domesticHotWater",
]);
</script>

<template>
  <SeawaterCircuitInstance
    x="1039.2832"
    y="782.916"
    v-bind="seawaterCircuits['drives:seawater']"
  />
  <ExchangeCircuitInstance
    x="1314"
    y="19.916"
    :height="183"
    v-bind="exchangeCircuits['drives:domesticHotWater']"
  />
</template>
