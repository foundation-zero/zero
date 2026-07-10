<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import PressureSensor from "../components/pressure-sensor/PressureSensor.vue";
import { getMimicDataProvider } from "../providers";
const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.PressureSensor>
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.PressureSensor"
    :data="props"
  >
    <PressureSensor
      v-bind="props"
      :state="state"
    />
  </MimicTooltipTrigger>
</template>
