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
import ConnectingCircuitInstance from "../../../instances/ConnectingCircuitInstance.vue";
import { LoopCircuitInstance } from "../../../instances/index.ts";
import { DHW_MIMIC_DATA } from "../data/index.ts";

const circuits = DHW_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const connectingCircuits = DHW_MIMIC_DATA[MimicComponentType.ConnectingCircuit];
</script>

<template>
  <g>
    <LoopCircuitInstance
      x="0"
      y="25"
      force-height
      v-bind="circuits['highTempLoop']"
    />
    <LoopCircuitInstance
      x="397"
      y="728"
      force-height
      v-bind="circuits['dcConverters']"
    />
    <LoopCircuitInstance
      x="650"
      y="728"
      force-height
      v-bind="circuits['drives']"
    />
    <LoopCircuitInstance
      x="903"
      y="728"
      force-height
      v-bind="circuits['adsorption']"
    />
    <ConnectingCircuitInstance
      x="1215"
      y="455"
      force-height
      height="300"
      v-bind="connectingCircuits['freshwater']"
    />
  </g>
</template>
