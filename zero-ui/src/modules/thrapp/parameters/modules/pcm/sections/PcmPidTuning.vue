<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { PidControllerTuning, pidControllerTuning } from "../../..";
import PidControllerCard from "../../../components/pid-controller-card/PidControllerCard.vue";

const controllers: PidControllerTuning[] = [
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "module1FlowController",
    "module1FlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "module2FlowController",
    "module2FlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "module3FlowController",
    "module3FlowBalanceTuning",
    ratioToPercentage,
  ),
  pidControllerTuning(
    "pcm",
    SensorComponentType.Flow,
    "module4FlowController",
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
