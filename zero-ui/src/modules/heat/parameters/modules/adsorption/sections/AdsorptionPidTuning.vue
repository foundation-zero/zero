<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/heat-simulation/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "adsorption",
    SensorComponentType.Temperature,
    "adsorptionHotMixController",
    "hotMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "adsorption",
    SensorComponentType.Temperature,
    "adsorptionRecoveryController",
    "recoveryTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "adsorption",
    SensorComponentType.Temperature,
    "adsorptionWasteCoolingController",
    "wasteCoolingTuning",
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
