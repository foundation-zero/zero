<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersHeatDumpController",
    "heatDumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersWarmupMixController",
    "warmupMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Flow,
    "thrustersPumpController",
    "pumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersAftRecoveryTemperatureController",
    "aftTemperatureTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersFwdRecoveryTemperatureController",
    "fwdTemperatureTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Flow,
    "thrustersAftFlowController",
    "aftFlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Flow,
    "thrustersFwdFlowController",
    "fwdFlowBalanceTuning",
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
