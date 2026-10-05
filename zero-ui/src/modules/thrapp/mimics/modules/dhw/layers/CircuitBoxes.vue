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
import { FreshwaterCircuitInstance, LoopCircuitInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const circuits = DHW_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const FreshwaterCircuits = DHW_MIMIC_DATA[MimicComponentType.FreshwaterCircuit];
</script>

<template>
  <g>
    <LoopCircuitInstance
      x="0"
      y="25"
      force-height
      height="195"
      v-bind="circuits['highTempLoop']"
    />
    <LoopCircuitInstance
      x="397"
      y="708"
      force-height
      height="220"
      v-bind="circuits['dcConverters']"
    />
    <LoopCircuitInstance
      x="650"
      y="708"
      force-height
      height="165"
      v-bind="circuits['drives']"
    />
    <LoopCircuitInstance
      x="903"
      y="708"
      force-height
      height="165"
      v-bind="circuits['adsorption']"
    />
    <FreshwaterCircuitInstance
      x="1215"
      y="455"
      force-height
      height="300"
      v-bind="FreshwaterCircuits['freshwater']"
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
