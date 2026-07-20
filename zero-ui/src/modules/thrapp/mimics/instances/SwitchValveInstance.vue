<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import SwitchValve from "../components/actuated-valve/SwitchValve.vue";
import TwoWayValve from "../components/actuated-valve/TwoWayValve.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.SwitchValve>
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.source);
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.SwitchValve"
    :data="props"
  >
    <ActuatedValve
      v-bind="props"
      :state="state"
      :rotation="1 - (valve?.positionRel.value ?? 0)"
    >
      <SwitchValve />
      <TwoWayValve :flow="valve?.positionRel.value ?? 0" />
    </ActuatedValve>
    <slot />
  </MimicTooltipTrigger>
</template>
