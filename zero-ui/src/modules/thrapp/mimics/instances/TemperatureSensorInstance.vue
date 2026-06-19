<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import TemperatureSensor from "../components/temperature-sensor/TemperatureSensor.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.TemperatureSensor>
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.TemperatureSensor"
    :data="props"
  >
    <TemperatureSensor
      v-bind="props"
      :state="state"
    />
  </MimicTooltipTrigger>
</template>
