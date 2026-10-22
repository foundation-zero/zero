<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import PressureSensor from "../components/pressure-sensor/PressureSensor.vue";
import { getMimicDataProvider } from "../providers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";
const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.LevelSensor>
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <PressureSensor
      v-bind="forwardedProps"
      :state="state"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
