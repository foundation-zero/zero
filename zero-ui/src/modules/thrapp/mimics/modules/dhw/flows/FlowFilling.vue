<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types/index.ts";
import { getField } from "../../../providers/index.ts";
import AnimatedCircuit from "./AnimatedCircuit.vue";
import AnimatedPipe from "./AnimatedPipe.vue";
import BaseFilling from "./BaseFilling.vue";
import FillingLT1 from "./FillingLT1.vue";
import FillingLT2 from "./FillingLT2.vue";
import Tank1Filling from "./Tank1Filling.vue";
import Tank2Filling from "./Tank2Filling.vue";
import Tank3Filling from "./Tank3Filling.vue";

const switchTank1 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Inlet");
const switchTank2 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Inlet");
const switchTank3 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Inlet");
const flowControlLT1 = getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc");
const flowControlLT2 = getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives");
const flowLT1 = getField(SensorComponentType.Flow, "dhw", "dhwFlowDc");
const flowLT2 = getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives");
</script>

<template>
  <AnimatedCircuit :flow="[flowLT1, flowLT2]">
    <AnimatedPipe :valves="[switchTank1, switchTank2, switchTank3]">
      <BaseFilling
        x="373"
        y="286"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[flowControlLT1]">
      <FillingLT1
        y="487"
        x="373"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[flowControlLT2]">
      <FillingLT2
        y="493"
        x="378"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank1]">
      <Tank1Filling
        x="377.5"
        y="146"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank2]">
      <Tank2Filling
        x="378"
        y="145"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank3]">
      <Tank3Filling
        x="378"
        y="145"
      />
    </AnimatedPipe>
  </AnimatedCircuit>
</template>
