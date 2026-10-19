<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { ExchangeCircuitInstance, SeawaterCircuitInstance } from "../../../instances";

const seawaterCircuits = getTooltipContexts(MimicComponentType.SeawaterCircuit, ["dc:seawater"]);
const exchangeCircuits = getTooltipContexts(MimicComponentType.ExchangeCircuit, [
  "dc:domesticHotWater",
]);
</script>

<template>
  <SeawaterCircuitInstance
    x="815.1406"
    y="570.1563"
    height="95"
    v-bind="seawaterCircuits['dc:seawater']"
  />
  <ExchangeCircuitInstance
    x="1403"
    y="274.1458"
    height="183"
    v-bind="exchangeCircuits['dc:domesticHotWater']"
  />
</template>
