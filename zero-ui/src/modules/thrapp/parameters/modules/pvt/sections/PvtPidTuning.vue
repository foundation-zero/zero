<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtHeatDumpController",
    "heatDumpTuning",
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainAftWarmupMixController",
    "mainAftMixTuning",
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainAftPumpController",
    "mainAftPumpTuning",
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainFwdWarmupMixController",
    "mainFwdMixTuning",
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainFwdPumpController",
    "mainFwdPumpTuning",
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtOwnersWarmupMixController",
    "ownersMixTuning",
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtOwnersPumpController",
    "ownersPumpTuning",
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
