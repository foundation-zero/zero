<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning("dhw", SensorComponentType.Flow, "dhwDcFlowController", "dcFlowTuning"),
  pidControllerTuning(
    "dhw",
    SensorComponentType.Flow,
    "dhwDrivesFlowController",
    "drivesFlowTuning",
  ),
  pidControllerTuning("dhw", SensorComponentType.Flow, "dhwPumpFlowController", "pumpFlowTuning"),
];
</script>

<template>
  <PidControllerCard
    v-for="controller in controllers"
    :key="controller.controller[2]"
    v-bind="controller"
  />
</template>
