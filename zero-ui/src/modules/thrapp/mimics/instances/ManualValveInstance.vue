<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ManualValveProps } from "../components/manual-valve";
import ManualValve from "../components/manual-valve/ManualValve.vue";

const props = defineProps<
  MimicComponentInstanceProps &
    ManualValveProps &
    TooltipComponentContext<MimicComponentType.ManualValve>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <ManualValve v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
