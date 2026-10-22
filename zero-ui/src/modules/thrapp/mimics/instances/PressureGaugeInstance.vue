<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import PressureGauge from "../components/pressure-gauge/PressureGauge.vue";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.PressureGauge>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <PressureGauge v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
