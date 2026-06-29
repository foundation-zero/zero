<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import { getField } from "../../../providers/index.ts";
import AnimatedCircuit from "./AnimatedCircuit.vue";
import AnimatedPipe from "./AnimatedPipe.vue";
import BaseBoosting from "./BaseBoosting.vue";
import BoostHeatpump from "./BoostHeatpump.vue";
import BoostHT from "./BoostHT.vue";
import BoostLT from "./BoostLT.vue";
import Tank1Boosting from "./Tank1Boosting.vue";
import Tank2Boosting from "./Tank2Boosting.vue";
import Tank3Boosting from "./Tank3Boosting.vue";

const flowBoosting = getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting");
const switchTank1 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply");
const switchTank2 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingSupply");
const switchTank3 = getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingSupply");
const switchHeatpump = getField(SensorComponentType.Valve, "dhw", "dhwSwitchHeatpump");
const switchHT = getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature");
const switchLT = getField(SensorComponentType.Valve, "dhw", "dhwSwitchLowTemperature");
</script>

<template>
  <AnimatedCircuit :flow="[flowBoosting]">
    <BaseBoosting
      x="130"
      y="226"
    />

    <AnimatedPipe :valves="[switchTank1]">
      <Tank1Boosting
        x="430"
        y="144"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank2]">
      <Tank2Boosting
        x="435"
        y="144"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchTank3]">
      <Tank3Boosting
        x="435"
        y="144"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchHeatpump]">
      <BoostHeatpump
        x="129"
        y="537"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchHT]">
      <BoostHT
        x="44"
        y="489"
      />
    </AnimatedPipe>

    <AnimatedPipe :valves="[switchLT]">
      <BoostLT
        x="197"
        y="566"
      />
    </AnimatedPipe>
  </AnimatedCircuit>
</template>
