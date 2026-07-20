<script setup lang="ts">
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import SwitchValve from "../components/actuated-valve/SwitchValve.vue";
import ThreeWayValve from "../components/actuated-valve/ThreeWayValve.vue";
import { getMimicDataProvider } from "../providers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ThreeWaySwitchValve>
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.source);
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ThreeWaySwitchValve"
    :data="props"
  >
    <ActuatedValve
      v-bind="props"
      :state="state"
    >
      <SwitchValve />
      <ThreeWayValve :flow="valve?.positionRel.value ?? 0" />
    </ActuatedValve>
    <slot />
  </MimicTooltipTrigger>
</template>
