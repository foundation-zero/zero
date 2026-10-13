<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import PressureGauge from "../components/pressure-gauge/PressureGauge.vue";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.PressureGauge>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.PressureGauge"
    :data="props"
  >
    <PressureGauge v-bind="props" />
    <slot />
  </MimicTooltipTrigger>
</template>
