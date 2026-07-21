<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import LevelSensor from "../components/level-sensor/LevelSensor.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.LevelSensor>
>();
const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.LevelSensor"
    :data="props"
  >
    <LevelSensor
      v-bind="props"
      :state="state"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
