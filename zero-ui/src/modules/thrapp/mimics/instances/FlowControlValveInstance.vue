<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import MixValve from "../components/actuated-valve/MixValve.vue";
import TwoWayValve from "../components/actuated-valve/TwoWayValve.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.FlowControlValve>
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.sensors.valve);
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.FlowControlValve"
    :data="props"
  >
    <ActuatedValve
      v-bind="props"
      :state="state"
    >
      <TwoWayValve :flow="valve?.positionRel.value ?? 0" />
      <MixValve />
    </ActuatedValve>
  </MimicTooltipTrigger>
</template>
