<script setup lang="ts">
/**
 * Circuit Boxes Layer
 *
 * Displays circuit information boxes for High Temp Loop, DC Converters, Drives, and Adsorption.
 * Uses the LoopCircuitInstance component to render each box with real-time temperature and flow data.
 *
 * FIGMA_URL: https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=7149:66096
 */

import { MimicComponentType } from "@/modules/thrapp/types";
import { RiArrowDownLine, RiArrowLeftLine } from "@remixicon/vue";
import { getTooltipContexts } from "../../../data";
import { ExchangeCircuitInstance, FreshwaterCircuitInstance } from "../../../instances";

const circuits = getTooltipContexts(MimicComponentType.ExchangeCircuit, [
  "dhw:highTempLoop",
  "dhw:dcConverters",
  "dhw:drives",
  "dhw:adsorption",
]);
const freshwaterCircuits = getTooltipContexts(MimicComponentType.FreshwaterCircuit, [
  "dhw:freshwater",
]);
</script>

<template>
  <g>
    <ExchangeCircuitInstance
      x="0"
      y="25"
      height="165"
      v-bind="circuits['dhw:highTempLoop']"
    />
    <ExchangeCircuitInstance
      x="397"
      y="708"
      height="165"
      v-bind="circuits['dhw:dcConverters']"
    />
    <ExchangeCircuitInstance
      x="650"
      y="708"
      height="165"
      v-bind="circuits['dhw:drives']"
    />
    <ExchangeCircuitInstance
      x="903"
      y="708"
      height="165"
      v-bind="circuits['dhw:adsorption']"
    />
    <FreshwaterCircuitInstance
      x="1215"
      y="455"
      height="196"
      v-bind="freshwaterCircuits['dhw:freshwater']"
    >
      <template #fromIcon>
        <RiArrowDownLine class="text-muted-foreground size-3" />
      </template>
      <template #toIcon>
        <RiArrowLeftLine class="text-muted-foreground size-3" />
      </template>
    </FreshwaterCircuitInstance>
  </g>
</template>
