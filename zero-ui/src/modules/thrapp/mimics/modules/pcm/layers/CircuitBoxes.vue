<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { RiArrowLeftLine, RiArrowRightLine, RiArrowUpLine } from "@remixicon/vue";
import { getTooltipContexts } from "../../../data";
import ConnectingCircuitInstance from "../../../instances/ConnectingCircuitInstance.vue";
import ExchangeCircuitInstance from "../../../instances/ExchangeCircuitInstance.vue";

const circuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, [
  "pcm:pvt",
  "pcm:thrusters",
  "pcm:freshwater",
]);
const exchangeCircuits = getTooltipContexts(MimicComponentType.ExchangeCircuit, [
  "pcm:dhw",
  "pcm:adsorption",
]);
</script>

<template>
  <ConnectingCircuitInstance
    x="-93"
    y="290"
    force-height
    height="193"
    v-bind="circuits['pcm:pvt']"
    inverted
  >
    <template #fromIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowLeftLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <ConnectingCircuitInstance
    x="112"
    y="290"
    force-height
    height="193"
    v-bind="circuits['pcm:thrusters']"
    inverted
  >
    <template #fromIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <ConnectingCircuitInstance
    x="1400"
    y="35"
    force-height
    height="168"
    v-bind="circuits['pcm:freshwater']"
    inverted
  >
    <template #fromIcon>
      <RiArrowRightLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowLeftLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <ExchangeCircuitInstance
    x="1400"
    y="222"
    force-height
    height="185"
    v-bind="exchangeCircuits['pcm:dhw']"
  />
  <ExchangeCircuitInstance
    x="1400"
    y="440"
    force-height
    height="168"
    v-bind="exchangeCircuits['pcm:adsorption']"
    :tooltip="exchangeCircuits['pcm:adsorption'].tooltip"
  />
</template>
