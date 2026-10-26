<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ExpansionTank } from "../components/expansion-tank";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ExpansionTank>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <ExpansionTank v-bind="forwardedProps" />
    <slot />
  </MimicTooltipTrigger>
</template>
