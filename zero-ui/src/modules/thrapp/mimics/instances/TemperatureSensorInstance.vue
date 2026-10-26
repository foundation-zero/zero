<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
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
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <TemperatureSensor
      v-bind="forwardedProps"
      :state="state"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
