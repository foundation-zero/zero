<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ExpansionValve } from "../components/expansion-valve";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ExpansionValve>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <ExpansionValve v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
