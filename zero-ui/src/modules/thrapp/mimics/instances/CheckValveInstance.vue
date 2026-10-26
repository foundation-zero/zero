<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import CheckValve from "../components/check-valve/CheckValve.vue";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.CheckValve>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <CheckValve v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
