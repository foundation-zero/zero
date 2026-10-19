<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HTMLWrapper } from "../components/html-wrapper";
import SeawaterCircuitContent from "./content/SeawaterCircuitContent.vue";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.SeawaterCircuit> & {
        width?: number | string;
        height?: number | string;
      }
  >(),
  { height: 90 },
);
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <HTMLWrapper v-bind="{ width, height, x, y }">
      <SeawaterCircuitContent v-bind="forwardedProps" />
    </HTMLWrapper>
  </MimicTooltipTrigger>
</template>
