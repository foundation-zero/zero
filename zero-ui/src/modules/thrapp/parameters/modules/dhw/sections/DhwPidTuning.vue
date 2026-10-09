<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "dhw",
    SensorComponentType.Temperature,
    "dhwDcFlowController",
    "dcFlowTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dhw",
    SensorComponentType.Temperature,
    "dhwDrivesFlowController",
    "drivesFlowTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "dhw",
    SensorComponentType.Flow,
    "dhwPumpFlowController",
    "pumpFlowTuning",
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
