<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import FlowSensor from "../components/flow-sensor/FlowSensor.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.FlowSensor>
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.FlowSensor"
    :data="props"
  >
    <FlowSensor
      v-bind="props"
      :state="state"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
