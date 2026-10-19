<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AirTrapVessel } from "../components/air-trap-vessel";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.AirTrapVessel>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <AirTrapVessel v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
