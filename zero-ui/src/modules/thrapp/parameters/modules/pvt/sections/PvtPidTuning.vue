<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtHeatDumpController",
    "heatDumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainAftWarmupMixController",
    "mainAftMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainAftPumpController",
    "mainAftPumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainFwdWarmupMixController",
    "mainFwdMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtMainFwdPumpController",
    "mainFwdPumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtOwnersWarmupMixController",
    "ownersMixTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pvt",
    SensorComponentType.Temperature,
    "pvtOwnersPumpController",
    "ownersPumpTuning",
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
