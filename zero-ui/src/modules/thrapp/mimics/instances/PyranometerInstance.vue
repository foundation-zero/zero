<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PyranoMeter } from "../components/pyrano-meter";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.Pyranometer>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Pyranometer"
    :data="props"
  >
    <PyranoMeter v-bind="props" />
    <slot />
  </MimicTooltipTrigger>
</template>
