<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AirTrapVessel } from "../components/air-trap-vessel";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.AirTrapVessel>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.AirTrapVessel"
    :data="props"
  >
    <AirTrapVessel v-bind="props" />
    <slot />
  </MimicTooltipTrigger>
</template>
