<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "drives",
    SensorComponentType.Temperature,
    "drivesHeatDumpController",
    "heatDumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "drives",
    SensorComponentType.Temperature,
    "drivesRecoveryMixController",
    "recoveryMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "drives",
    SensorComponentType.Flow,
    "drivesPumpControllerShorepower",
    "pumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "drives",
    SensorComponentType.Flow,
    "drivesPumpControllerPropulsion",
    "pumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "drives",
    SensorComponentType.Flow,
    "drivesAftFlowController",
    "aftFlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "drives",
    SensorComponentType.Flow,
    "drivesFwdFlowController",
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
