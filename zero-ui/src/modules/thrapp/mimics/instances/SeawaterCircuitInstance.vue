<script setup lang="ts">
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
        forceHeight?: boolean;
      }
  >(),
  { height: 90 },
);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.SeawaterCircuit"
    :data="props"
  >
    <HTMLWrapper v-bind="{ width, height, forceHeight, x, y }">
      <SeawaterCircuitContent
        v-bind="{ sensors, controllerState, controls, parameters, source, tooltip, custom }"
      />
    </HTMLWrapper>
  </MimicTooltipTrigger>
</template>
