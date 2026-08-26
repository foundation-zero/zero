<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types/index.ts";
import { getField } from "../../../providers/index.ts";
import AnimatedCircuit from "./AnimatedCircuit.vue";
import AnimatedPipe from "./AnimatedPipe.vue";
import Tank1InUse from "./Tank1InUse.vue";
import Tank2InUse from "./Tank2InUse.vue";
import Tank3InUse from "./Tank3InUse.vue";

const switchTank1 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Outlet");
const switchTank2 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Outlet");
const switchTank3 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Outlet");
const flowSupply = getField(SensorComponentType.Flow, "dhw", "freshwaterHotwaterFlow");
</script>

<template>
  <AnimatedCircuit :flow="[flowSupply]">
    <AnimatedPipe :valves="[switchTank1]">
      <Tank1InUse
        x="538"
        y="143"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank2]">
      <Tank2InUse
        y="145"
        x="890"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank3]">
      <Tank3InUse
        y="143.5"
        x="1231"
      />
    </AnimatedPipe>
  </AnimatedCircuit>
</template>
