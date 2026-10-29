<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExchangeCircuitInstance,
  FreshwaterCircuitInstance,
  SeawaterCircuitInstance,
} from "../../../instances";
import { RiArrowLeftLine } from "@remixicon/vue";

const exchangeCircuits = getTooltipContexts(MimicComponentType.ExchangeCircuit, [
  "adsorption:domesticHotWater",
  "adsorption:highTemperature",
]);
const freshwaterCircuits = getTooltipContexts(MimicComponentType.FreshwaterCircuit, [
  "adsorption:cooling",
]);
const seawaterCircuits = getTooltipContexts(MimicComponentType.SeawaterCircuit, [
  "adsorption:seawater",
]);
</script>

<template>
  <g>
    <ExchangeCircuitInstance
      x="0"
      y="12"
      width="196"
      height="174"
      v-bind="exchangeCircuits['adsorption:domesticHotWater']"
    />
    <ExchangeCircuitInstance
      x="1652"
      y="12"
      width="196"
      height="174"
      v-bind="exchangeCircuits['adsorption:highTemperature']"
    />
    <FreshwaterCircuitInstance
      x="1265"
      y="489"
      width="196"
      height="188"
      v-bind="freshwaterCircuits['adsorption:cooling']"
    >
      <template #toIcon>
        <RiArrowLeftLine class="text-muted-foreground size-3" />
      </template>
    </FreshwaterCircuitInstance>
    <SeawaterCircuitInstance
      x="369"
      y="559"
      width="196"
      height="95"
      v-bind="seawaterCircuits['adsorption:seawater']"
    />
  </g>
</template>
