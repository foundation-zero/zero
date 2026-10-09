<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersHeatDumpController",
    "heatDumpTuning",
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersWarmupMixController",
    "warmupMixTuning",
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Flow,
    "thrustersPumpController",
    "pumpTuning",
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersAftRecoveryTemperatureController",
    "aftTemperatureTuning",
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Temperature,
    "thrustersFwdRecoveryTemperatureController",
    "fwdTemperatureTuning",
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Flow,
    "thrustersAftFlowController",
    "aftFlowBalanceTuning",
  ),
  pidControllerTuning(
    "thrusters",
    SensorComponentType.Flow,
    "thrustersFwdFlowController",
    "fwdFlowBalanceTuning",
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
