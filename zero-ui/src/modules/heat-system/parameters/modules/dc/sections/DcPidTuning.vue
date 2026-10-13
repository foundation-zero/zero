<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/heat-system-simulation/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "dc",
    SensorComponentType.Temperature,
    "dcHeatDumpController",
    "heatDumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Temperature,
    "dcRecoveryMixController",
    "recoveryMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Flow,
    "dcBrightloopsAftPumpController",
    "brightloopsAftPumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Temperature,
    "dcBrightloopsAftWarmupMixController",
    "brightloopsAftMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Flow,
    "dcBrightloopsFwdPumpController",
    "brightloopsFwdPumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Temperature,
    "dcBrightloopsFwdWarmupMixController",
    "brightloopsFwdMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Flow,
    "dcUgridsPumpController",
    "ugridsPumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dc",
    SensorComponentType.Temperature,
    "dcUgridsWarmupMixController",
    "ugridsMixTuning",
    ratioToPercentage,
  ),
];
</script>

<template>
  <PidControllerCard
    v-for="controller in controllers"
    :key="controller.controller[2]"
    v-bind="controller"
  />
</template>
