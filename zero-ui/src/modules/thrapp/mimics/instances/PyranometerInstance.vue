<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PyranoMeter } from "../components/pyrano-meter";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.Pyranometer>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <PyranoMeter v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
