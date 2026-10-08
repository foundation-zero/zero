<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ConnectingCircuitInstance, SeawaterCircuitInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const seaWaterCircuits = THRUSTERS_MIMIC_DATA[MimicComponentType.SeawaterCircuit];
const connectingCircuits = THRUSTERS_MIMIC_DATA[MimicComponentType.ConnectingCircuit];
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="1002"
      y="316"
      force-height
      height="195"
      v-bind="connectingCircuits?.['pcm']"
    />

    <SeawaterCircuitInstance
      x="595"
      y="20"
      width="194"
      height="85"
      force-height
      v-bind="seaWaterCircuits?.['seawater']"
    />
  </g>
</template>
