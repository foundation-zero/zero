<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/heat-system-simulation/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "pcmPumpFlowController",
    "pumpTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "pcmModule1FlowController",
    "module1FlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "pcmModule2FlowController",
    "module2FlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "pcmModule3FlowController",
    "module3FlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "pcmModule4FlowController",
    "module4FlowBalanceTuning",
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
