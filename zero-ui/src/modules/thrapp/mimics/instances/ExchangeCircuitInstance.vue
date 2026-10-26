<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HTMLWrapper } from "../components/html-wrapper";
import ExchangeCircuit from "./content/ExchangeCircuitContent.vue";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.ExchangeCircuit> & {
        width?: number | string;
        height?: number | string;
      }
  >(),
  {
    width: 196,
    height: 200,
    forceHeight: true,
  },
);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <HTMLWrapper v-bind="{ width, height, x, y }">
      <ExchangeCircuit
        class="w-full"
        v-bind="{ sensors, controllerState, controls, parameters, source, tooltip, custom }"
      />
    </HTMLWrapper>
    <slot />
  </MimicTooltipTrigger>
</template>
